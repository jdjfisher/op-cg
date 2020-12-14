
# Standard library imports
import re

# Third party imports
from clang.cindex import Index, Config
import clang.cindex as cindex

# Local application imports
from parsers.common import Store, ParseError
from util import enumRegex


# TODO: Generalise config
Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-10.so.1")
index = Index.create()


def parse(path):
  # Invoke the Clang parser on the source
  translation_unit = index.parse(path)

  # Initialise the store and search queue
  store = Store()
  q = []

  # Populate with the top-level cursors from the target file
  for child in translation_unit.cursor.get_children():
    if child.location.file.name == translation_unit.spelling:
      q.append(child)

  # BFS
  while q:
    
    # Manage the queue
    node = q.pop()
    q.extend(node.get_children())

    # 
    if node.kind == cindex.CursorKind.CALL_EXPR:
      name = node.spelling

      if name == 'op_init_base':
        parseInit(node)

      elif name == 'op_decl_set':
        parseSet(node)
      
      elif name == 'op_decl_map':
        parseMap(node)
      
      elif name == 'op_decl_dat':
        parseData(node)
      
      elif name == 'op_decl_const':
        parseConst(node)

      elif name == 'op_par_loop':
        store.addLoop(parseLoop(node))

      elif name == 'op_exit':
        pass

  return store


def parseInit(node):
  pass


def parseSet(node):
  pass


def parseMap(node):
  pass


def parseData(node):
  pass


def parseConst(node):
  pass


def parseLoop(node):
  nodes = list(node.get_children())[1:]

  if len(nodes) < 3:
    raise ParseError('incorrect number of args passed to op_par_loop')

  # Parse loop kernel and set
  kernel = nodes[0].spelling
  # _ = parseStringLit(nodes[1])
  set_ = nodes[2]

  loop_args = []

  # Parse loop args
  for node in nodes[3:]:
    node = descend(descend(node))
    name = node.spelling
    args = list(node.get_children())

    if name == 'op_arg_dat':
      loop_args.append(parseArgDat(args))

    elif name == 'op_opt_arg_dat':
      loop_args.append(parseOptArgDat(args))

    elif name == 'op_arg_gbl':
      loop_args.append(parseArgGbl(args))

    elif name == 'op_opt_arg_gbl':
      loop_args.append(parseOptArgGbl(args))

    else:
      raise ParseError(f'Invalid loop argument {name}')

  return {
    # 'locations': [],
    'kernel'   : kernel,
    'set'      : set_,
    'args'     : loop_args,
  }


def parseArgDat(nodes):
  nodes = nodes[1:]

  if len(nodes) != 6:
    raise ParseError('incorrect number of args passed to op_arg_dat')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(['OP_READ','OP_WRITE','OP_RW','OP_INC'])

  # Parse each arg
  var  = parseIdentifier(nodes[0])
  idx  = parseIntLit(nodes[1], signed=True)
  # map_ = parseIdentifier(nodes[2])
  dim  = parseIntLit(nodes[3], signed=False)
  typ  = parseStringLit(nodes[4], regex=type_regex)
  # acc  = parseIdentifier(nodes[5], regex=access_regex)

  exit()
  # return { 'var': var, 'idx': idx, 'map': map_, 'dim': dim, 'typ': typ, 'acc': acc }


def parseOptArgDat(node):
  pass


def parseArgGbl(node):
  pass


def parseOptArgGbl(node):
  pass


def parseIdentifier(node, regex=None):

  # Validate the node
  if node.kind != cindex.CursorKind.UNEXPOSED_EXPR:
    raise ParseError('expected identifier')

  # Descend to child node
  node = descend(node)

  # Validate the node
  if node.kind != cindex.CursorKind.DECL_REF_EXPR:
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
  if signed and node.kind == cindex.CursorKind.UNARY_OPERATOR and next(node.get_tokens()).spelling == '-': 
    negation = True
    node = descend(node)

  # Validate the node
  if node.kind != cindex.CursorKind.INTEGER_LITERAL:
    if not signed:
      raise ParseError('expected unsigned integer literal')
    else:
      raise ParseError('expected integer literal')

  # Extract the value
  value = int(next(node.get_tokens()).spelling)

  return -value if negation else value


def parseStringLit(node, regex=None):

  # Validate the node
  if node.kind != cindex.CursorKind.UNEXPOSED_EXPR:
    raise ParseError('expected string literal')

  # Descend to child node
  node = descend(node)

  # Validate the node
  if node.kind != cindex.CursorKind.STRING_LITERAL:
    raise ParseError('expected string literal')

  # Extract value from string delimeters
  value = node.spelling[1:-1]

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected string literal matching {regex}')

  return value


def descend(node):
  # TODO: Add a check
  return next(node.get_children(), None)
  