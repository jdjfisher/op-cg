
# Standard library imports
import re
import json

# Third party imports
import open_fortran_parser as fp


class Store:
  def __init__(self, init=None, exit=False, consts=[], loops=[]):
    self.init = init
    self.exit = exit
    self.consts = consts
    self.loops = loops

  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"


def parse(path):  
  # try:
  xml = fp.parse(path, raise_on_error=True)
  # xml.write("temp/dump.xml")
  # except :
  #   print('f')

  # Create a store
  store = Store()

  # Iterate over all Call AST nodes
  for call in xml.findall('.//call'):

    # Store call source location
    location = call.attrib
    name = parseIdentifier(call)

    if call.find('name').attrib['type'] == 'procedure':
      args = call.findall('name/subscripts/subscript')

      if name == 'op_init_base':
        parseInit(args)
      elif name == 'op_decl_set':
        parseSet(args)
      elif name == 'op_decl_map':
        parseMap(args)
      elif name == 'op_decl_dat':
        parseData(args)
      elif name == 'op_decl_const':
        parseConst(args)
      elif re.search(r'op_par_loop_[1-9]\d*', name):
        parseLoop(args)

  return Store()


def parseInit(args):
  if len(args) != 2:
    raise Exception()

  _ = parseIntLit(args[0], signed=False)
  _ = parseIntLit(args[1], signed=False)

  return


def parseSet(args):
  pass


def parseMap(args):
  pass


def parseData(args):
  pass


def parseConst(args):
  if len(args) != 3:
    raise Exception()

  return {
    'name' : parseIdentifier(args[0]),
    'dim'  : parseIntLit(args[1], signed=False),
    'name2': parseStringLit(args[2]),
  }


def parseLoop(args):
  if len(args) < 3:
    raise Exception()

  actions = []

  # Parse loop actions
  for action in args[2:]: 
    name = parseIdentifier(action)
    action_args = action.findall('name/subscripts/subscript')

    if name == 'op_arg_dat':
      parseArgDat(action_args)
    elif name == 'op_opt_arg_dat':
     parseOptArgDat(action_args)
    elif name == 'op_arg_gbl':
      parseArgGbl(action_args)
    elif name == 'op_opt_arg_gbl':
      parseOptArgGbl(action_args)
    else:
      raise Exception()
      
  return {
    'kernel' : parseIdentifier(args[0]),
    'set'    : parseIdentifier(args[1]),
    'actions': actions
  }


def parseArgDat(args):
  if len(args) != 6:
    raise Exception()

  return {
    'dat': parseIdentifier(args[0]),
    'idx': parseIntLit(args[1], signed=True),
    'map': parseIdentifier(args[2]),
    'dim': parseIntLit(args[3], signed=False),
    'typ': parseStringLit(args[4]),
    'acc': parseIdentifier(args[5]),
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







