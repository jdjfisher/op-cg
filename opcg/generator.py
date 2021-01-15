
# Standard library imports
from typing import Tuple, Dict, List
from os.path import basename
import json
import re

# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

# Local application imports
from parsers.common import Store
from optimisation import Opt
from language import Lang
import optimisation
import language
import op as OP


# Jinja configuration
env = Environment(
  loader=FileSystemLoader('resources/templates'),
  lstrip_blocks=True,
  trim_blocks=True,
)

env.globals['enumerate'] = enumerate
env.globals['any'] = any
env.tests['r_o_w_acc'] = lambda arg: arg.acc in (OP.READ, OP.WRITE)
env.tests['rw_acc'] = lambda arg: arg.acc == OP.RW
env.tests['inc_acc'] = lambda arg: arg.acc == OP.INC
env.tests['without_dim'] = lambda arg: not isinstance(arg.dim, int) 
env.tests['global'] = lambda arg: arg.global_
env.tests['direct'] = lambda arg: arg.direct
env.tests['indirect'] = lambda arg: arg.indirect




# TODO: Make more robust
templates: Dict[Tuple[Lang, Opt], Template] = {
  (language.f, optimisation.seq): env.get_template('fortran/seq.F90.j2'),
  (language.f, optimisation.cuda): env.get_template('fortran/cuda.F90.j2'),
  (language.c, optimisation.seq): env.get_template('cpp/seq.hpp.j2'),
}



# Augment source program to use generated kernel hosts
def genOpProgram(lang: Lang, opt: Opt, source: str, store: Store, soa: bool = False) -> str:
  
  # TODO: Abstract to callable
  if lang.name == 'fortran':
    lines = source.splitlines(True)

    # 1. Comment-out const calls
    for const in store.consts:
      lines[const.loc.line - 1] = lang.com_delim + ' ' + lines[const.loc.line - 1]

    # 2. Update loop calls
    for loop in store.loops:
      before, after = re.split(r'op_par_loop_[1-9]\d*', lines[loop.loc.line - 1], 1)
      after = after.replace(loop.name, f'"{loop.name}"') # TODO: This assumes that the kernel arg is on the same line as the call
      lines[loop.loc.line - 1] = before + f'op_par_loop_{loop.name}_host' + after

    source = ''.join(lines)

    # 3. Update init call
    if soa:
      _ = re.search(r'op_(mpi_)?init', source) # TODO: Finish

    # 4. Update headers
    before, after = source.split('  use OP2_Fortran_Reference\n', 1) # TODO: Make more robust
    for loop in store.loops:
      before += f'  use {opt.name}_{loop.name}_module\n' 

    source = before + after

  elif lang.name == 'c++':
    # 1. Update const calls
    # 2. Update loop calls
    # 3. Update init call
    # 4. Update headers
    pass

  return source


# 
def genLoopHost(lang: Lang, opt: Opt, loop: OP.Loop, i: int) -> str:
  # Lookup generation template
  template = templates.get((lang, opt))

  if not template:
    exit(f'template not found for {lang.name}-{opt.name}')

  # Generate source from the template
  return template.render(kernel=loop, opt=opt, id=i)


# 
def genMakefile(paths: List[str]) -> str:
  # Lookup generation template
  template = env.get_template('makefile.j2')

  files = [ basename(path) for path in paths ]

  return template.render(files=files)
