
# Standard imports
import re

# Third party imports
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
  lines[index] = line.replace(kernel.name, kernel.name + '_gpu')

  needs_istat = False

  # Atomize incremenal assignments
  if self.opt.config['atomics']:
    for assignment in body.findall('.//assignment'):
      # Traverse AST
      name = assignment.find('target/name').attrib['id']
      operands = assignment.findall('value/operation/operand')
      operator = assignment.find('value/operation/operator/add-op')

      # Determine if the assignment is a valid increment that should be atomised 
      atomise = name is not None and operator is not None and \
        len(operands) == 2 and name in increments and \
        any(o.find('name') and o.find('name').attrib['id'] == name for o in operands)

      if atomise:
        # Extract source locations from AST
        line_index = int(assignment.attrib['line_begin']) - 1
        assignment_offset = int(assignment.attrib['col_begin']) - 1
        value_offset = int(assignment.find('value').attrib['col_begin']) - 1
        operator_offset = int(operator.attrib['col_begin']) - 1

        # Fold continuations
        line = lines[line_index].rstrip()
        continuations = 0
        while line.endswith('&'):
          continuations += 1
          line = line[:-1] + lines[line_index + continuations].lstrip()[1:]

        # Compute indentation string
        indent = (assignment_offset + 1) * ' '

        # Atomize the assignment
        _, value = indexSplit(line, value_offset)
        l, r = indexSplit(value, operator_offset - value_offset)
        line = indent + 'istat = AtomicAdd(' + l.strip() + ', ' + r.strip() + ')'
        lines[line_index] = line

        # Remove old continuations
        for i in range(1, continuations + 1):
          lines[line_index + i] = indent
   
        needs_istat = True

    # Insert istat typing
    if needs_istat:
      spec = body.find('specification')
      indent = ' ' * int(spec.attrib['col_begin'])
      lines.insert(int(spec.attrib['line_end']), indent + 'INTEGER(kind=4) :: istat(4)')

  # Augment OP2 constant references
  source = '\n'.join(lines)
  for const in app.consts:
    source = source.replace(const.ptr, const.ptr + '_OP2')

  return source
