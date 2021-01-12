
# Standard library imports
import json
import os

# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

# Local application imports
from optimisation import Opt
from language import Lang
from parsers.common import Store
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




# TODO: Improve
templates: {(str, str): Template} = {
  ('fortran', 'seq'): env.get_template('fortran/seq.F90.j2'),
  ('fortran', 'cuda'): env.get_template('fortran/cuda.F90.j2'),
  ('c++', 'seq'): env.get_template('cpp/seq.hpp.j2'),
}




# Augment source program to use generated kernel hosts
def genOpProgram(lang: Lang, source: str, store: Store) -> str: 
  
  # TODO: Abstract to callable
  if lang.name == 'fortran':
    pass
  elif lang.name == 'c++':
    pass

  # 1. Update headers
  # 2. Update init call
  # 3. Remove const calls
  # 4. Update loop calls
  return source


# 
def genLoopHost(lang: Lang, opt: Opt, loop: OP.Loop, i: int) -> str:
  # Lookup generation template
  template = templates.get((lang.name, opt.name))

  if not template:
    exit(f'template not found for {lang.name}-{opt.name}')

  # Generate source from the template
  return template.render(kernel=loop, id=i)


# 
def genMakefile(paths: [str]) -> str:
  # 
  template = env.get_template('makefile.j2')

  files = map(os.path.basename, paths)

  return template.render(files=files)