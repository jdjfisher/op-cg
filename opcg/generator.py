
# Standard library imports
from typing import Tuple, Dict, List
from pathlib import Path
import json
import os

# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

# Local application imports
from store import Store
from optimisation import Opt
from language import Lang
import optimisation
import op as OP
import fortran
import cpp


# Jinja configuration
env = Environment(
  loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../resources/templates')),
  lstrip_blocks=True,
  trim_blocks=True,
)

env.tests['r_or_w_acc'] = lambda arg: arg.acc in (OP.READ, OP.WRITE)
env.tests['rw_acc'] = lambda arg: arg.acc == OP.RW
env.tests['inc_acc'] = lambda arg: arg.acc == OP.INC
env.tests['without_dim'] = lambda arg: not isinstance(arg.dim, int) 
env.tests['global'] = lambda arg: arg.global_
env.tests['direct'] = lambda arg: arg.direct
env.tests['indirect'] = lambda arg: arg.indirect


# TODO: Make more robust
templates: Dict[Tuple[Lang, Opt], Path] = {
  (fortran.lang, optimisation.seq): Path('fortran/seq.F90.j2'),
  (fortran.lang, optimisation.cuda): Path('fortran/cuda.CUF.j2'),
  (cpp.lang, optimisation.seq): Path('cpp/seq.cpp.j2'),
}


# 
def genLoopHost(lang: Lang, opt: Opt, loop: OP.Loop, i: int) -> Tuple[str, str]:
  # Lookup generation template
  path = templates.get((lang, opt))

  if not path:
    exit(f'template not found for {lang.name}-{opt.name}')

  template = env.get_template(str(path))
  extension = path.suffixes[-2][1:]

  # Generate source from the template
  return template.render(parloop=loop, id=i), extension


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
