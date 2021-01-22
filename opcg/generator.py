
# Standard library imports
from typing import Tuple, Dict, List
from pathlib import Path
import json
import re
import os

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
  loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../resources/templates')),
  lstrip_blocks=True,
  trim_blocks=True,
)

env.globals['any'] = any
env.tests['r_or_w_acc'] = lambda arg: arg.acc in (OP.READ, OP.WRITE)
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
  (language.c, optimisation.seq): env.get_template('cpp/seq.cpp.j2'),
}



# Augment source program to use generated kernel hosts
def genOpProgram(lang: Lang, source: str, store: Store, soa: bool = False) -> str:
  lines = source.splitlines(True)


  # TODO: Abstract
  if lang.name == 'fortran':
    # 1. Comment-out const calls
    for const in store.consts:
      lines[const.loc.line - 1] = lang.com_delim + ' ' + lines[const.loc.line - 1]

    # 2. Update loop calls
    for loop in store.loops:
      before, after = re.split(r'op_par_loop_[1-9]\d*', lines[loop.loc.line - 1], 1)
      after = after.replace(loop.kernel, f'"{loop.kernel}"') # TODO: This assumes that the kernel arg is on the same line as the call
      lines[loop.loc.line - 1] = before + f'op_par_loop_{loop.name}_host' + after

    # 3. Update headers
    index = lines.index('  use OP2_Fortran_Reference\n')  # TODO: Make more robust
    for loop in store.loops:
      lines.insert(index, f'  use {loop.name.upper()}_MODULE\n') 

    # 4. Update init call TODO: Use a line number from the store
    source = ''.join(lines)
    if soa:
      source = re.sub(r'\bop_init(\w*)\b\s*\((.*)\)','op_init\\1_soa(\\2,1)', source)
      source = re.sub(r'\bop_mpi_init(\w*)\b\s*\((.*)\)','op_mpi_init\\1_soa(\\2,1)', source)


  elif lang.name == 'c++':
    # 1. Update const calls
    for const in store.consts:
      lines[const.loc.line - 1] = re.sub(
        r'op_decl_const\s*\(',
        f'op_decl_const2("{const.debug}", ',
        lines[const.loc.line - 1]
      )

    # 2. Update loop calls
    for loop in store.loops:
      before, after = lines[loop.loc.line - 1].split('op_par_loop', 1)
      after = re.sub(f'{loop.kernel}\s*,\s*', '', after, count=1) # TODO: This assumes that the kernel arg is on the same line as the call
      lines[loop.loc.line - 1] = before + f'op_par_loop_{loop.name}_host' + after

    # 3. Update headers
    index = lines.index('#include "op_seq.h"\n') + 2 # TODO: Make more robust
    for loop in store.loops:
      prototype = f'void op_par_loop_{loop.name}_host(char const *, op_set{", op_arg" * len(loop.args)});\n'
      lines.insert(index, prototype)

    # 4. Update init call TODO: Use a line number from the store
    source = ''.join(lines)
    if soa:
      source = re.sub(r'\bop_init\b\s*\((.*)\)','op_init_soa(\\1,1)', source)
      source = re.sub(r'\bop_mpi_init\b\s*\((.*)\)','op_mpi_init_soa(\\1,1)', source)

  return source


# 
def genLoopHost(lang: Lang, opt: Opt, loop: OP.Loop, i: int) -> str:
  # Lookup generation template
  template = templates.get((lang, opt))

  if not template:
    exit(f'template not found for {lang.name}-{opt.name}')

  # Generate source from the template
  return template.render(parloop=loop, id=i)


# 
def genMakefile(opt: Opt, paths: List[Path]) -> str:
  # Lookup generation template
  template = env.get_template('makefile.j2')

  source_files = [ path.name for path in paths ]
  object_files = [ path.with_suffix('.o') for path in paths ]

  return template.render(
    source_files=source_files,
    object_files=object_files,
    opt=opt,
  )
