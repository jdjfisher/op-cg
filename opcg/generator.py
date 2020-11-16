
# Standard library imports
import json

# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

# Local application imports
from util import replaceCode
import parallelization as para
import language as lang


# Jinja configuration
env = Environment(
  loader=FileSystemLoader('resources/templates'),
  lstrip_blocks=True,
  trim_blocks=True,
)


# TODO: Improve
schemes = {
  ('Fortran', 'seq') : env.get_template('fortran/seq.F90.j2')
}


def augmentProgram(source, store):
  # Augment source program to use generated parrallelisations
  # 1. Update headers
  # 2. Update init call
  # 3. Remove const calls
  # 4. Update loop calls
  return source


def genKernelHost(lang, para, kernel):
  # Lookup generation template
  template = schemes.get((lang.name, para.name))

  # Exit if the template was not found
  if not template:
    raise Exception('TODO: ...')

  # Generate source from the template
  return template.render(kernel=kernel)