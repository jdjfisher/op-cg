
# Standard library imports
from subprocess import CalledProcessError
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

    # Create a store
    store = Store()

    # Iterate over all Call AST nodes
    for call in xml.findall('.//call'):

      # Store call source location
      location = call.attrib
      name = parseIdentifier(call)

      if call.find('name').attrib['type'] == 'procedure':
        # Collect the call arg nodes
        args = call.findall('name/subscripts/subscript')

        if name == 'op_init_base':
          store.recordInit(parseInit(args, location))

        elif name == 'op_decl_set':
          _ = parseSet(args)

        elif name == 'op_decl_map':
          _ = parseMap(args)

        elif name == 'op_decl_dat':
          _ = parseData(args)

        elif name == 'op_decl_const':
          store.addConst(parseConst(args, location))

        elif re.search(r'op_par_loop_[1-9]\d*', name):
          store.addLoop(parseLoop(args, location))

        elif name == 'op_exit':
          store.recordExit(location)

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


def parseSet(args):
  if len(args) != 3:
    raise Exception()

  return {
    'size': parseIdentifier(args[0]),
    'name': parseIdentifier(args[1]),
    'str' : parseStringLit(args[2]),
  }


def parseMap(args):
  if len(args) != 6:
    raise Exception()

  return {

  }


def parseData(args):
  if len(args) != 6:
    raise Exception()

  return {
    
  }


def parseConst(args, location):
  if len(args) != 3:
    raise Exception()

  return {
    'location': location,
    'name'    : parseIdentifier(args[0]),
    'dim'     : parseIntLit(args[1], signed=False),
    'str'     : parseStringLit(args[2]),
  }


def parseLoop(args, location):
  if len(args) < 3:
    raise Exception()

  actions = []

  # Parse loop actions
  for action in args[2:]: 
    name = parseIdentifier(action)
    action_args = action.findall('name/subscripts/subscript')

    if name == 'op_arg_dat':
      actions.append(parseArgDat(action_args))

    elif name == 'op_opt_arg_dat':
      actions.append(parseOptArgDat(action_args))

    elif name == 'op_arg_gbl':
      actions.append(parseArgGbl(action_args))

    elif name == 'op_opt_arg_gbl':
      actions.append(parseOptArgGbl(action_args))

    else:
      raise Exception(f'Invalid loop argument {name}')
      
  return {
    'location': location,
    'kernel'  : parseIdentifier(args[0]),
    'set'     : parseIdentifier(args[1]),
    'actions' : actions,
  }


def parseArgDat(args):
  if len(args) != 6:
    raise Exception()

  # Regex for valid op loop data types TODO: finish
  type_regex = r'".*"'

  # Regex for valid op loop action access types 
  access_regex = enumRegex(['OP_READ','OP_WRITE','OP_RW','OP_INC','OP_MAX','OP_MIN'])


  return {
    'dat': parseIdentifier(args[0]),
    'idx': parseIntLit(args[1], signed=True),
    'map': parseIdentifier(args[2]),
    'dim': parseIntLit(args[3], signed=False),
    'typ': parseStringLit(args[4], regex=type_regex),
    'acc': parseIdentifier(args[5], regex=access_regex),
  }


def parseOptArgDat(args):
  if len(args) != 7:
    raise Exception()

  # Parse opt argument
  opt = parseIdentifier(args[0])

  # Parse standard argDat arguments
  dat = parseArgDat(args[1:])
  
  # Return augmented dat
  dat.update(opt=opt)
  return dat


def parseArgGbl(args):
  pass


def parseOptArgGbl(args):
  pass


def parseIdentifier(node, regex=None):
  # Move to child name node
  node = node.find('name')

  # Validate the node
  if not node or not node.attrib['id']:
    raise Exception('TODO: ...')

  value = node.attrib['id']

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise Exception('TODO: ...')
  
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
    raise Exception('TODO: ...')

  # Return the integer value of the literal
  value = int(node.attrib['value'])
  return -value if negation else value


def parseStringLit(node, regex=None):
  # Move to child literal node
  node = node.find('literal')

  # Validate the node
  if not node or node.attrib['type'] != 'char':
    raise Exception('TODO: ...')

  value = node.attrib['value']

  # Apply conditional regex constraint
  if regex and not re.match(regex, value):
    raise Exception('TODO: ...')
  
  return value







