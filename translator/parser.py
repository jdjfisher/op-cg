
# Standard library imports
import re, json
from subprocess import call

# Application imports
from util import extractDelimStr


access_labels = ['OP_READ', 'OP_WRITE', 'OP_RW', 'OP_INC', 'OP_MAX', 'OP_MIN']


class Store:
  def __init__(self, inits, exits, consts, loops):
    self.inits = inits
    self.exits = exits
    self.consts = consts
    self.loops = loops

  def __str__(self):
    return f'''{len(self.consts)} constants, {len(self.loops)} loops''' # TODO: ...


def parseProgram(data):
  # TODO: preprocess text to remove comments and line continuations

  return Store(
    inits  = parseInits(data),
    exits  = parseExits(data),
    consts = parseConsts(data),
    loops  = parseParLoops(data),
  )


def parseApiCalls(name_regex, text):
  # Regex for a call 
  regex = r'call\s+' + name_regex + r'\s*\(\s*'

  calls = []
  #
  for match in re.finditer(regex, text):

    # Extract call name
    name = re.search(name_regex, match.group()).group()

    # Extract call arguments 
    raw_args = extractDelimStr(text, ('(', ')'), match.start())
    args = [ a.strip() for a in re.split(r',(?!\S\)|\()', raw_args) ] # TODO: finish

    calls.append((name, args))

  return calls
  

def parseInits(text):
  return len(re.findall(r'op_init|op_init_base', text))
  

def parseExits(text):
  return len(re.findall(r'op_exit', text))


def parseConsts(text):
  consts = []

  # Iterate over all valid calls to op_decl_const
  for _, args in parseApiCalls('op_decl_const', text):

    # Store args
    consts.append({
      'name' : args[0],
      'dim'  : args[1],
      'name2': args[2],
    })

  return consts


def parseParLoops(text):
  loops = []

  # Iterate over all valid calls to op_par_loop_<int>
  for call, args in parseApiCalls(r'op_par_loop_[1-9][0-9]*', text):

    loops.append({
      'call': call,
      'kernel': args[0],
      'set': args[1],
      'args': args[2:],
      'direct': True, # TODO: ...
    })

  return loops

