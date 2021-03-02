
# Third part imports
from xml.etree.ElementTree import Element, dump
import json

# Application imports
from store import Kernel, Application
from util import indexSplit, find


def translateKernel(self, source: str, kernel: Kernel, app: Application) -> str:
  lines = source.splitlines()
  #print(lines[0])

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

  # Augment subroutine header with additional argument
  argument = kernel.ast.find('file/subroutine/header/arguments/argument')
  print(argument[0].attrib)
  #header = subroutine.find('header')
  #arguments = header.find('arguments')
  #argument = arguments.findall('argument')
  #print(arguments[0].attrib)
  #print(arguments.attrib)
  #print(arguments[1].attrib)
  #index = int(arguments[len(argument)].attrib['line_begin'])
  #indent = ' ' * int(arguments[1].attrib['col_begin'])
  #lines.insert(index, indent + 'idx2, ')
  #line = lines[index]

  #lines[index] = line.replace('x1', 'test')


  #lines[index] = line.replace(')', ',idx2)')

  #indent = ' ' * int(header.attrib['col_end'])
  #lines.insert(int(header.attrib['line_end']), indent + 'idx2')

  # Add additional argument - idx
  spec = body.find('specification')
  indent = ' ' * int(spec.attrib['col_begin'])
  lines.insert(int(spec.attrib['line_end']), indent + 'INTEGER(kind=4) :: idx')

  # Augment OP2 constant references
  source = '\n'.join(lines)
  for const in app.consts:
    source = source.replace(const.ptr, const.ptr + '_OP2')

  return source
