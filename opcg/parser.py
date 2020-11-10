
# Standard library imports
import re
import json
import os
import contextlib
from subprocess import call

# Third party imports
import open_fortran_parser as fp

# Application imports
from util import extractDelimStr


class Store:
  def __init__(self, init=0, exit=0, consts=[], loops=[]):
    self.init = init
    self.exit = exit
    self.consts = consts
    self.loops = loops


  def merge(self, store):
    self.init += store.init
    self.exit += store.exit
    self.consts += store.consts
    self.loops += store.loops


  def __str__(self):
    return f'''{len(self.consts)} constants, {len(self.loops)} loops''' # TODO: ...


def parseProgram(path):
  # with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
    # try:
  xml = fp.parse(path, raise_on_error=True)
  # xml = parser.parse([path], xml_generator_config)
    # except :
    #   print('oof')

  



  # for prog in xml.findall('program'):
  #   print(prog.tag)
 
  # return Store(
  #   init  = parseInits(data),
  #   exit  = parseExits(data),
  #   consts = parseConsts(data),
  #   loops  = parseParLoops(data),
  # )

  return


def parseApiCalls(name_regex, text):
  # Regex for a call 
  regex = r'call\s+' + name_regex + r'\s*\(\s*'

  calls = []
  #
  for match in re.finditer(regex, text):

    # Extract call name
    name = re.search(name_regex, match.group()).group()

    # Extract call arguments 
    args_str = extractDelimStr(text, ('(', ')'), match.start())
    raw_args = re.split(r',\s*(?![^()]*\))', args_str) # TODO: Deal with deep paranthesis
    args = [ re.sub(r'\s*&\s*\n\s*&\s*', '', a) for a in raw_args ]  # TODO: cleanup, generalise for language

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

