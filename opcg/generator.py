
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

directTest = lambda arg: arg.get('map') == OP.ID
directFilter = lambda args: filter(directTest, args)

env.globals['enumerate'] = enumerate
env.globals['any'] = any
env.globals['direct'] = directFilter
env.tests['r_o_w_acc'] = lambda arg: arg.get('acc') in (OP.READ, OP.WRITE)
env.tests['rw_acc'] = lambda arg: arg.get('acc') == OP.RW
env.tests['inc_acc'] = lambda arg: arg.get('acc') == OP.INC
env.tests['without_dim'] = lambda arg: not isinstance(arg.get('dim'), int) 
env.tests['global'] = lambda arg: 'map' not in arg
env.tests['direct'] = directTest
env.tests['indirect'] = lambda arg: 'map' in arg and arg.get('map') != OP.ID




# TODO: Improve
templates = {
  ('fortran', 'seq'): env.get_template('fortran/seq.F90.j2'),
  ('fortran', 'cuda'): env.get_template('fortran/cuda.F90.j2'),
  ('c++', 'seq'): env.get_template('cpp/seq.hpp.j2'),
}


# Augment source program to use generated kernel hosts
def genOpProgram(source: str, store: Store): 
  # 1. Update headers
  # 2. Update init call
  # 3. Remove const calls
  # 4. Update loop calls
  return source


# 
def genKernelHost(lang: Lang, opt: Opt, kernel):
  # Lookup generation template
  template = templates.get((lang.name, opt.name))

  if not template:
    exit(f'template not found for {lang.name}-{opt.name}')

  # Generate source from the template
  return template.render(kernel=kernel)


# 
def genMakefile(paths):
  # 
  template = env.get_template('makefile.j2')

  files = map(os.path.basename, paths)

  return template.render(files=files)