
# Third party imports
from clang.cindex import Index, Config
import clang.cindex

# Local application imports
from parsers.common import Store, ParseError


# TODO: Generalise
Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-10.so.1")


def parse(path):
  index = Index.create()
  translation_unit = index.parse(path)

  q = []

  for child in translation_unit.cursor.get_children():
    if child.location.file.name == translation_unit.spelling:
      q.append(child)

  while q:
    cursor = q.pop()
    q.extend(cursor.get_children())

    if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
      name = cursor.spelling

      if name == 'op_init_base':
        pass

      elif name == 'op_decl_set':
        pass
      
      elif name == 'op_decl_map':
        pass
      
      elif name == 'op_decl_dat':
        pass
      
      elif name == 'op_decl_const':
        pass

      elif name == 'op_par_loop':
        pass

      elif name == 'op_exit':
        pass


  exit('w.i.p')

  return Store()


def parseInit():
  pass


def parseSet():
  pass


def parseMap():
  pass


def parseData():
  pass


def parseConst():
  pass


def parseLoop():
  pass


def parseArgDat(args):
  pass


def parseOptArgDat(args):
  pass


def parseArgGbl(args):
  pass


def parseOptArgGbl(args):
  pass