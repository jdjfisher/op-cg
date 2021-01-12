
# Standard library imports
from subprocess import CalledProcessError
from xml.etree.ElementTree import Element
# import xml.etree.ElementTree as ET
import re

# Third party imports
import open_fortran_parser as fp

# Local application imports
from parsers.common import ParseError, Store, Location
from util import enumRegex
import op as OP


def parse(path: str) -> Store:  
  try:
    # Try to parse the source
    xml = fp.parse(path, raise_on_error=True)
    # ET.dump(xml)

    # Create a store
    store = Store()

    # Iterate over all Call AST nodes
    for call in xml.findall('.//call'):

      # Store call source location
      loc = parseLocation(call)
      name = parseIdentifier(call)

      if call.find('name').attrib['type'] == 'procedure':
        # Collect the call arg nodes
        args = call.findall('name/subscripts/subscript')

        if name == 'op_init_base':
          store.recordInit()

        elif name == 'op_decl_set':
          store.addSet(parseSet(args, loc))

        elif name == 'op_decl_map':
          store.addMap(parseMap(args, loc))

        elif name == 'op_decl_dat':
          store.addData(parseData(args, loc))

        elif name == 'op_decl_const':
          store.addConst(parseConst(args, loc))

        elif re.search(r'op_par_loop_[1-9]\d*', name):
          store.addLoop(parseLoop(args, loc))

        elif name == 'op_exit':
          store.recordExit()

    # Return the store
    return store

  # Catch ofp error
  except CalledProcessError as error:
    raise ParseError(error.output)


def parseSet(nodes: [Element], location: Location) -> OP.Set:
  if len(nodes) != 3:
    raise ParseError('incorrect number of nodes passed to op_decl_set', location)

  size = parseIdentifier(nodes[0])
  name = parseIdentifier(nodes[1])
  
  return OP.Set(name, size)


def parseMap(nodes: [Element], location: Location) -> OP.Map:
  if len(nodes) != 6:
    raise ParseError('incorrect number of args passed to op_decl_map', location)

  _   = parseIdentifier(nodes[0])
  _   = parseIdentifier(nodes[1])
  dim = parseIntLit(nodes[2], signed=False)
  _   = parseIdentifier(nodes[3])
  _   = parseIdentifier(nodes[4])

  return OP.Map(dim)


def parseData(nodes: [Element], location: Location) -> OP.Data:
  if len(nodes) != 6:
    raise ParseError('incorrect number of args passed to op_decl_dat', location)

  set_ = parseIdentifier(nodes[0])
  dim  = parseIntLit(nodes[1], signed=False)
  typ  = parseStringLit(nodes[2])
  _    = parseIdentifier(nodes[3])
  _    = parseIdentifier(nodes[4])

  return OP.Data(set_, dim, typ)
  

def parseConst(nodes: [Element], location: Location) -> OP.Const:
  if len(nodes) != 3:
    raise ParseError('incorrect number of args passed to op_decl_const', location)

  name = parseIdentifier(nodes[0])
  dim = parseIntLit(nodes[1], signed=False)

  return OP.Const(name, dim)


def parseLoop(nodes: [Element], location: Location):
  if len(nodes) < 3:
    raise ParseError('incorrect number of args passed to op_par_loop', location)

  # Parse loop kernel and set
  kernel = parseIdentifier(nodes[0])
  set_   = parseIdentifier(nodes[1])

  loop_args = []

  # Parse loop args
  for raw_arg in nodes[2:]: 
    name = parseIdentifier(raw_arg)
    args = raw_arg.findall('name/subscripts/subscript')

    if name == 'op_arg_dat':
      loop_args.append(parseArgDat(args))

    elif name == 'op_opt_arg_dat':
      loop_args.append(parseOptArgDat(args))

    elif name == 'op_arg_gbl':
      loop_args.append(parseArgGbl(args))

    elif name == 'op_opt_arg_gbl':
      loop_args.append(parseOptArgGbl(args))

    else:
      raise ParseError(f'invalid loop argument {name}')

  return {
    'locations': [location],
    'kernel'   : kernel,
    'set'      : set_,
    'args'     : loop_args,
  }


def parseArgDat(nodes: [Element]):
  if len(nodes) != 6:
    raise ParseError('incorrect number of args passed to op_arg_dat')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(OP.DAT_ACCESS_TYPES)

  return {
    'var': parseIdentifier(nodes[0]),
    'idx': parseIntLit(nodes[1], signed=True),
    'map': parseIdentifier(nodes[2]),
    'dim': parseIntLit(nodes[3], signed=False),
    'typ': parseStringLit(nodes[4], regex=type_regex),
    'acc': parseIdentifier(nodes[5], regex=access_regex),
  }


def parseOptArgDat(nodes: [Element]):
  if len(nodes) != 7:
    ParseError('incorrect number of args passed to op_opt_arg_dat')

  # Parse opt argument
  opt = parseIdentifier(nodes[0])

  # Parse standard argDat arguments
  dat = parseArgDat(nodes[1:])
  
  # Return augmented dat
  dat.update(opt=opt)
  return dat


def parseArgGbl(nodes: [Element]):
  if len(nodes) != 4:
    raise ParseError('incorrect number of args passed to op_arg_gbl')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(OP.GBL_ACCESS_TYPES)
  
  return {
    'var': parseIdentifier(nodes[0]),
    'dim': parseIntLit(nodes[1], signed=False),
    'typ': parseStringLit(nodes[2], regex=type_regex),
    'acc': parseIdentifier(nodes[3], regex=access_regex),
  }
  

def parseOptArgGbl(nodes: [Element]):
  if len(nodes) != 5:
    ParseError('incorrect number of args passed to op_opt_arg_gbl')

  # Parse opt argument
  opt = parseIdentifier(nodes[0])

  # Parse standard argGbl arguments
  dat = parseArgGbl(nodes[1:])
  
  # Return augmented dat
  dat.update(opt=opt)
  return dat


def parseIdentifier(node: [Element], regex: str = None) -> str:
  # Descend to child node
  node = node.find('name')

  # Validate the node
  if not node or not node.attrib['id']:
    raise ParseError('expected identifier', parseLocation(node))

  value = node.attrib['id']

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected identifier matching {regex}', parseLocation(node))
  
  return value


def parseIntLit(node: [Element], signed: bool = True) -> int:
  # Assume the literal is not negated
  negation = False

  # Check if the node is wrapped in a valid unary negation
  if signed and node.find('operation'):
    node = node.find('operation')
    if node.attrib['type'] == 'unary' and node.find('operator') and node.find('operator').attrib['operator'] == '-':
      negation = True
      node = node.find('operand')

  # Descend to child literal node
  node = node.find('literal')

  # Verify and typecheck the literal node
  if not node or node.attrib['type'] != 'int':
    location = parseLocation(node)

    if not signed:
      raise ParseError('expected unsigned integer literal', location)
    else:
      raise ParseError('expected integer literal', location)

  # Extract the value
  value = int(node.attrib['value'])

  return -value if negation else value


def parseStringLit(node: [Element], regex: str = None) -> str:
  # Descend to child literal node
  node = node.find('literal')

  # Validate the node
  if not node or node.attrib['type'] != 'char':
    raise ParseError('expected string literal', parseLocation(node))

  # Extract value from string delimeters
  value = node.attrib['value'][1:-1]

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected string literal matching {regex}', parseLocation(node))
  
  return value


def parseLocation(node: Element) -> Location:
  return Location(
    '?',
    node.attrib.get('line_begin'), 
    node.attrib.get('col_begin')
  )







