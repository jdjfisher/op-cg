
# Standard imports
import re
from typing import Tuple

# Third part imports
from xml.etree.ElementTree import Element, dump

# Application imports
from store import Kernel, Application
from util import SourceBuffer, indexSplit, find


def translateKernel(self, source: str, kernel: Kernel, app: Application) -> Tuple[str,int]:
  buffer = SourceBuffer(source)

  # Collect indirect increment identifiers TODO: Tidy
  loop = find(app.loops, lambda l: l.kernel == kernel.name)
  increments = []
  for param, arg in zip(kernel.params, loop.args):
    if arg.indirect and arg.acc == 'OP_INC':
      increments.append(param[0])

  #Check if this kernel is for an indirect loop
  ind = 0
  loop = find(app.loops, lambda l: l.kernel == kernel.name)
  for arg in loop.args:
    if arg.indirect:
      ind = ind + arg.indirect
      print(arg.var, arg.typ)

  #modify only indirect loops
  if ind :
    # Ast traversal
    subroutine = kernel.ast.find('file/subroutine')
    body = subroutine.find('body')

    # Augment kernel subroutine name
    index = int(subroutine.attrib['line_begin']) - 1
    buffer.apply(index, lambda line: line.replace(kernel.name, kernel.name + '_vec'))

    # Augment subroutine header with additional argument
    arguments = kernel.ast.find('file/subroutine/header/arguments')
    line_index = int(arguments.attrib['line_begin'])-1
    line = buffer.get(line_index).strip()
    continuations = 0
    while line.endswith('&'):
      continuations += 1
      line = line[:-1].strip() + buffer.get(line_index + continuations).strip()[1:].strip()

    #remove closing )
    i = line.find(')')
    line = line[:i-1]
    buffer.update(line_index, line.strip() + ",idx)")

    # Remove old continuations
    for i in range(1, continuations + 1):
      buffer.remove(line_index + i)

    # Add additional argument - idx
    spec = body.find('specification')
    indent = ' ' * int(spec.attrib['col_begin'])
    buffer.insert(int(spec.attrib['line_begin']), indent + 'INTEGER(kind=4) :: idx')

  return source, ind
