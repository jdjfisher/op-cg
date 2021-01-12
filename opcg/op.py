
ID = 'OP_ID'

INC   = 'OP_INC'
MAX   = 'OP_MAX'
MIN   = 'OP_MIN'
RW    = 'OP_RW'
READ  = 'OP_READ'
WRITE = 'OP_WRITE'

DAT_ACCESS_TYPES = [READ, WRITE, RW, INC]
GBL_ACCESS_TYPES = [READ, INC, MAX, MIN]


class Set:

  def __init__(self, name: str, size: int):
    self.name = name
    self.size = size


class Map:

  def __init__(self, dim: int):
    self.dim = dim
  

class Data:

  def __init__(self, set_: str, dim: int, typ: str):
    self.set = set_
    self.dim = dim
    self.typ = typ


class Const:

  def __init__(self, name: str, dim: int):
    self.name = name
    self.dim = dim


class Arg:

  def __init__(self, var: str, map_: str, idx: int, dim: int, typ: str, acc: str):
    self.var = var
    self.map = map_
    self.idx = idx
    self.dim = dim
    self.typ = typ
    self.acc = acc

    if self.map == ID:
      if self.idx != -1:
        exit('incompatible index for direct access, expected -1')
    else:
      if self.idx < 1 or self.idx > self.dim:
        exit(f'out of range index, must be 1-{self.dim}')


class Loop:

  def __init__(self, kernel: str, set_: str, args: [Arg]):
    self.kernel = kernel
    self.set = set_
    self.args = args
