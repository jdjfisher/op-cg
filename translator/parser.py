
# Standard library imports
import re, json
from subprocess import call

# Application imports
from util import markedSubstr


access_labels = ['OP_READ', 'OP_WRITE', 'OP_RW', 'OP_INC', 'OP_MAX', 'OP_MIN']


class ParseError(Exception):
  def __init__(self, message, filename, line):
      self.message = message
      self.filename = filename
      self.line = line
      super().__init__(f'ParserError: {filename} line: {line} {message}')


# def pre():
  # compiler_path = 'gfortran'
  # sources = ['examples/airfoil/op2_for_declarations.F90', './examples/airfoil/airfoil.F90']
  # return_code = call([compiler_path] + sources, shell=True)  
  # print(return_code)


def parse(data):
  # TODO: preprocess text to remove comments and line continuations

  data = {
    'inits': parseInits(data),
    'consts' : parseConsts(data),
    'loops' : parseParLoops(data),
    'exits': parseExits(data),
  }

  print(json.dumps(data, indent=2))
  return data


def parseApiCalls(name_regex, text):
  # Regex for a call 
  regex = r'call\s+' + name_regex + r'\s*\(\s*'

  calls = []
  #
  for match in re.finditer(regex, text):
    depth = 1
    i = match.end() 

    # Scan the text until the same depth closing paranthesis is found 
    while depth:
      if text[i] == '(':
        depth += 1
      elif text[i] == ')':
        depth -= 1
      i += 1

    # Extract call name
    name = re.search(name_regex, match.group()).group()

    # Extract call arguments TODO: factor in paranthesis
    args = [ a.strip() for a in text[ match.end() : i-1 ].split(',') ]

    calls.append((name, args))

  return calls
  

def parseInits(text):
  return len(re.findall(r'op_init|op_init_base', text))
  

def parseExits(text):
  return len(re.findall(r'op_exit', text))


# op_partition
def parseParts(text):
  pass


# hdf5
def parseHdf5s(text):
  pass


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
    })

  return loops

