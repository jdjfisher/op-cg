
# Third part imports
from xml.etree.ElementTree import Element, dump

# Application imports
from store import Kernel, Application
from util import indexSplit, find


def translateKernel(self, source: str, kernel: Kernel, app: Application) -> str:
  lines = source.splitlines()

  # Collect indirect increment identifiers TODO: Tidy
  loop = find(app.loops, lambda l: l.kernel == kernel.name)
  increments = []
  for param, arg in zip(kernel.params, loop.args):
    if arg.indirect and arg.acc == 'OP_INC':
      increments.append(param[0])

  # Ast traversal
  subroutine = kernel.ast.find('file/subroutine')
  body = subroutine.find('body')

  # Augment kernel subroutine name
  index = int(subroutine.attrib['line_begin']) - 1
  line = lines[index]
  lines[index] = line.replace(kernel.name, kernel.name + '_vec')

  # Add additional argument - idx
  spec = body.find('specification')
  indent = ' ' * int(spec.attrib['col_begin'])
  lines.insert(int(spec.attrib['line_end']), indent + 'INTEGER(kind=4) :: idx')

  # Augment OP2 constant references
  source = '\n'.join(lines)
  for const in app.consts:
    source = source.replace(const.ptr, const.ptr + '_OP2')

  return source
