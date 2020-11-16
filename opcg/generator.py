
# Standard library imports
import json

# Third party imports
from jinja2 import Template

# Local application imports
from util import replaceCode


# TODO: Store refs to transaltion functions for lang, para pairings
schemes = {
  # (fortran, seq) : seq.F90.j2
}


class Transaltion:
  pass


def augmentProgram(source, store):
  # Augment source program to use generated parrallelisations
  # 1. Update headers
  # 2. Update init call
  # 3. Remove const calls
  # 4. Update loop calls
  return source


def genKernelHost(kernel, scheme):
  # Load kernel host template
  template = Template(open(scheme).read())

  # Generate source from the template
  return template.render(kernel=kernel)