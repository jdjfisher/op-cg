
# Standard library imports
import re

# Third party imports
from clang.cindex import Index, Config, TranslationUnit, CursorKind
import clang.cindex as cindex

# Local application imports
from parsers.common import ParseError, Store, Location
from util import enumRegex
import op as OP


# TODO: Generalise config
Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-10.so.1")
options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD # Capture pre-processor macros
index = Index.create()


def parse(path):
  # Invoke the Clang parser on the source
  translation_unit = index.parse(path, options=options)

  # Throw the parse error first parse error caught in the diagnostics 
  error = next(iter(translation_unit.diagnostics), None)
  if error:
    raise ParseError(error.spelling, parseLocation(error))

  # Initialise the store and search queue
  store = Store()
  q = []

  # Populate with the top-level cursors from the target file
  for child in translation_unit.cursor.get_children():
    if child.kind in (CursorKind.MACRO_INSTANTIATION, CursorKind.MACRO_DEFINITION):
      pass # TODO: ...
    elif child.location.file.name == translation_unit.spelling:
      q.append(child)

  # BFS
  while q:
    
    # Manage the queue
    node = q.pop()
    q.extend(node.get_children())

    # Focus on function calls
    if node.kind == CursorKind.CALL_EXPR:
      name = node.spelling
      args = list(node.get_children())[1:]
      loc = parseLocation(node)

      if name == 'op_init_base':
        store.recordInit()

      elif name == 'op_decl_set':
        parseSet(args, loc)
      
      elif name == 'op_decl_map':
        parseMap(args, loc)
      
      elif name == 'op_decl_dat':
        parseData(args, loc)
      
      elif name == 'op_decl_const':
        store.addConst(parseConst(args, loc))

      elif name == 'op_par_loop':
        store.addLoop(parseLoop(args, loc))

      elif name == 'op_exit':
        store.recordExit()

  return store


def parseSet(nodes, location):
  if len(nodes) != 2:
    raise ParseError('incorrect number of nodes passed to op_decl_set', location)

  return {
    'size': parseIdentifier(nodes[0]),
    'str' : parseStringLit(nodes[1]),
  }


def parseMap(nodes, location):
  if len(nodes) != 5:
    raise ParseError('incorrect number of args passed to op_decl_map', location)

  return {
    'x'   : parseIdentifier(nodes[0]),
    'y'   : parseIdentifier(nodes[1]),
    'dim' : parseIntLit(nodes[2], signed=False),
    'z'   : parseIdentifier(nodes[3]),
    'str' : parseStringLit(nodes[4]),
  }


def parseData(nodes, location):
  if len(nodes) != 5:
    raise ParseError('incorrect number of args passed to op_decl_dat', location)

  return {
    'set' : parseIdentifier(nodes[0]),
    'dim' : parseIntLit(nodes[1], signed=False),
    'typ' : parseStringLit(nodes[2]),
    'x'   : parseIdentifier(nodes[3]),
    'str' : parseStringLit(nodes[4]),
  }


def parseConst(nodes, location):
  if len(nodes) != 3:
    raise ParseError('incorrect number of args passed to op_decl_const', location)

  return {
    'locations': [],
    'dim'      : parseIntLit(nodes[0], signed=False),
    'str'      : parseStringLit(nodes[1]),
    'name'     : parseIdentifier(nodes[2]),
  }


def parseLoop(nodes, location):
  if len(nodes) < 3:
    raise ParseError('incorrect number of args passed to op_par_loop')

  # Parse loop kernel and set
  kernel = parseIdentifier(nodes[0])
  _  = parseStringLit(nodes[1])
  set_ = parseIdentifier(nodes[2]) 

  loop_args = []

  # Parse loop args
  for node in nodes[3:]:
    node = descend(descend(node))
    name = node.spelling
    args = list(node.get_children())[1:]

    if name == 'op_arg_dat':
      loop_args.append(parseArgDat(args))

    elif name == 'op_opt_arg_dat':
      loop_args.append(parseOptArgDat(args))

    elif name == 'op_arg_gbl':
      loop_args.append(parseArgGbl(args))

    elif name == 'op_opt_arg_gbl':
      loop_args.append(parseOptArgGbl(args))

    else:
      raise ParseError(f'invalid loop argument {name}', parseLocation(node))

  return {
    'locations': [],
    'kernel'   : kernel,
    'set'      : set_,
    'args'     : loop_args,
  }


def parseArgDat(nodes):
  if len(nodes) != 6:
    raise ParseError('incorrect number of args passed to op_arg_dat')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(OP.DAT_ACCESS_TYPES)

  return {
    'var': parseIdentifier(nodes[0]),
    'idx': parseIntLit(nodes[1], signed=True),
    'map': parseIdentifier(nodes[2]) or OP.ID,
    'dim': parseIntLit(nodes[3], signed=False),
    'typ': parseStringLit(nodes[4], regex=type_regex),
    'acc': OP.READ, #parseIdentifier(nodes[5]) # TODO: Fix
  }


def parseOptArgDat(nodes):
  if len(nodes) != 7:
    ParseError('incorrect number of args passed to op_opt_arg_dat')

    # Parse opt argument
    opt = parseIdentifier(nodes[0])

    # Parse standard argDat arguments
    dat = parseArgDat(nodes[1:])
    
    # Return augmented dat
    dat.update(opt=opt)
    return dat


def parseArgGbl(nodes):
  if len(nodes) != 4:
    raise ParseError('incorrect number of args passed to op_arg_gbl')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(OP.GBL_ACCESS_TYPES)

  return {
    'var': parseIdentifier(nodes[0]),
    'dim': parseIntLit(nodes[1], signed=False),
    'typ': parseStringLit(nodes[2], regex=type_regex),
    'acc': OP.READ, # parseIdentifier(nodes[3]),  # TODO: Fix
  }


def parseOptArgGbl(nodes):
  if len(nodes) != 5:
    raise ParseError('incorrect number of args passed to op_opt_arg_gbl')

    # Parse opt argument
    opt = parseIdentifier(nodes[0])

    # Parse standard argGbl arguments
    dat = parseArgGbl(nodes[1:])
    
    # Return augmented dat
    dat.update(opt=opt)
    return dat


def parseIdentifier(node, regex=None):
  # TODO: ...
  while node.kind == CursorKind.CSTYLE_CAST_EXPR:
    node = list(node.get_children())[1]

  # Descend to child node
  if node.kind == CursorKind.UNEXPOSED_EXPR:
    node = descend(node)

  # Descend to child node
  if node.kind == CursorKind.UNARY_OPERATOR and next(node.get_tokens()).spelling in ('&', '*'):
    node = descend(node)

  # Check for null
  if node.kind == CursorKind.GNU_NULL_EXPR:
    return None

  # Validate the node
  if node.kind != CursorKind.DECL_REF_EXPR:
    raise ParseError('expected identifier')

  value = node.spelling

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected identifier matching {regex}')

  return value


def parseIntLit(node, signed=True):
  # Assume the literal is not negated
  negation = False

  # Check if the node is wrapped in a valid unary negation 
  if signed and node.kind == CursorKind.UNARY_OPERATOR and next(node.get_tokens()).spelling == '-': 
    negation = True
    node = descend(node)

  # Validate the node
  if node.kind != CursorKind.INTEGER_LITERAL:
    if not signed:
      raise ParseError('expected unsigned integer literal')
    else:
      raise ParseError('expected integer literal')

  # Extract the value
  value = int(next(node.get_tokens()).spelling)

  return -value if negation else value


def parseStringLit(node, regex=None):

  # Validate the node
  if node.kind != CursorKind.UNEXPOSED_EXPR:
    raise ParseError('expected string literal')

  # Descend to child node
  node = descend(node)

  # Validate the node
  if node.kind != CursorKind.STRING_LITERAL:
    raise ParseError('expected string literal')

  # Extract value from string delimeters
  value = node.spelling[1:-1]

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected string literal matching {regex}')

  return value


def parseLocation(node):
  return Location(
    node.location.file.name,
    node.location.line,
    node.location.column
  )


def descend(node):
  return next(node.get_children(), None)
  