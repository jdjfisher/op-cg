
# Standard library imports
from subprocess import CalledProcessError
# import xml.etree.ElementTree as ET
import re
import json

# Third party imports
import open_fortran_parser as fp

# Local application imports
from parsers.common import Store, ParseError
from util import enumRegex


def parse(path):  
  try:
    # Try to parse the source
    xml = fp.parse(path, raise_on_error=True)
    # ET.dump(xml)

    # Create a store
    store = Store()

    # Iterate over all Call AST nodes
    for call in xml.findall('.//call'):

      # Store call source location
      loc = call.attrib
      name = parseIdentifier(call)

      if call.find('name').attrib['type'] == 'procedure':
        # Collect the call arg nodes
        args = call.findall('name/subscripts/subscript')

        if name == 'op_init_base':
          store.recordInit(parseInit(args, loc))

        elif name == 'op_decl_set':
          _ = parseSet(args, loc)

        elif name == 'op_decl_map':
          _ = parseMap(args, loc)

        elif name == 'op_decl_dat':
          _ = parseData(args, loc)

        elif name == 'op_decl_const':
          store.addConst(parseConst(args, loc))

        elif re.search(r'op_par_loop_[1-9]\d*', name):
          store.addLoop(parseLoop(args, loc))

        elif name == 'op_exit':
          store.recordExit(loc)

    # Return the store
    return store

  # Catch ofp error
  except CalledProcessError as error:
    raise ParseError(error.output)


def parseInit(args, location):
  if len(args) != 2:
    raise ParseError('incorrect number of args passed to op_init', location)

  _ = parseIntLit(args[0], signed=False)
  _ = parseIntLit(args[1], signed=False)

  return {
    'location': location,
  }


def parseSet(args, location):
  if len(args) != 3:
    raise ParseError('incorrect number of args passed to op_decl_set', location)

  return {
    'size': parseIdentifier(args[0]),
    'name': parseIdentifier(args[1]),
    'str' : parseStringLit(args[2]),
  }


def parseMap(args, location):
  if len(args) != 6:
    raise ParseError('incorrect number of args passed to op_decl_map', location)

  return {

  }


def parseData(args, location):
  if len(args) != 6:
    raise ParseError('incorrect number of args passed to op_decl_dat', location)

  return {
    
  }


def parseConst(args, location):
  if len(args) != 3:
    raise ParseError('incorrect number of args passed to op_decl_const', location)

  return {
    'locations': [location],
    'name'     : parseIdentifier(args[0]),
    'dim'      : parseIntLit(args[1], signed=False),
    'str'      : parseStringLit(args[2]),
  }


def parseLoop(args, location):
  if len(args) < 3:
    raise ParseError('incorrect number of args passed to op_par_loop', location)

  # Parse loop kernel and set
  kernel = parseIdentifier(args[0])
  set_   = parseIdentifier(args[1])

  loop_args = []

  # Parse loop args
  for raw_arg in args[2:]: 
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
      raise ParseError(f'Invalid loop argument {name}')

  return {
    'locations': [location],
    'kernel'   : kernel,
    'set'      : set_,
    'args'     : loop_args,
  }


def parseArgDat(args):
  if len(args) != 6:
    raise ParseError('incorrect number of args passed to op_arg_dat')

  type_regex = r'.*' # TODO: Finish ...
  access_regex = enumRegex(['OP_READ','OP_WRITE','OP_RW','OP_INC'])

  # Parse each arg
  var  = parseIdentifier(args[0])
  idx  = parseIntLit(args[1], signed=True)
  map_ = parseIdentifier(args[2])
  dim  = parseIntLit(args[3], signed=False)
  typ  = parseStringLit(args[4], regex=type_regex)
  acc  = parseIdentifier(args[5], regex=access_regex)

  # Check arg compatibility
  if map_ == 'OP_ID' and idx != -1:
    raise Exception('incompatible index for direct access, expected -1')

  return { 'var': var, 'idx': idx, 'map': map_, 'dim': dim, 'typ': typ, 'acc': acc }


def parseOptArgDat(args):
  if len(args) != 7:
    ParseError('incorrect number of args passed to op_opt_arg_dat')

  # Parse opt argument
  opt = parseIdentifier(args[0])

  # Parse standard argDat arguments
  dat = parseArgDat(args[1:])
  
  # Return augmented dat
  dat.update(opt=opt)
  return dat


def parseArgGbl(args):
  if len(args) != 4:
    raise ParseError('incorrect number of args passed to op_arg_gbl')

  # Regex for valid op loop data types TODO: finish
  type_regex = r'.*'

  # Regex for valid global op loop action access types 
  access_regex = enumRegex(['OP_READ','OP_INC','OP_MAX','OP_MIN'])
  
  return {
    'var': parseIdentifier(args[0]),
    'dim': parseIntLit(args[1], signed=False),
    'typ': parseStringLit(args[2], regex=type_regex),
    'acc': parseIdentifier(args[3], regex=access_regex),
  }
  

def parseOptArgGbl(args):
  if len(args) != 5:
    ParseError('incorrect number of args passed to op_opt_arg_gbl')

  # Parse opt argument
  opt = parseIdentifier(args[0])

  # Parse standard argGbl arguments
  dat = parseArgGbl(args[1:])
  
  # Return augmented dat
  dat.update(opt=opt)
  return dat


def parseIdentifier(node, regex=None):
  # Move to child name node
  node = node.find('name')

  # Validate the node
  if not node or not node.attrib['id']:
    raise ParseError('expected identifier')

  value = node.attrib['id']

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected identifier matching {regex}')
  
  return value


def parseIntLit(node, signed=True):
  # Assume the literal is not negated
  negation = False

  # Check if the node is wrapped in a valid unary negation
  if signed and node.find('operation'):
    node = node.find('operation')
    if node.attrib['type'] == 'unary' and node.find('operator') and node.find('operator').attrib['operator'] == '-':
      node = node.find('operand')
      negation = True

  # Move to child literal node
  node = node.find('literal')

  # Verify and typecheck the literal node
  if not node or node.attrib['type'] != 'int':
    if not signed:
      raise ParseError('expected unsigned integer literal')
    else:
      raise ParseError('expected integer literal')

  # Return the integer value of the literal
  value = int(node.attrib['value'])
  return -value if negation else value


def parseStringLit(node, regex=None):
  # Move to child literal node
  node = node.find('literal')

  # Validate the node
  if not node or node.attrib['type'] != 'char':
    raise ParseError('expected string literal')

  # Extract value from string delimeters
  value = node.attrib['value'][1:-1]

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise ParseError(f'expected string literal matching {regex}')
  
  return value







