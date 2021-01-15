# Standard library imports
from typing import Optional, Dict, List

ID = 'OP_ID'

INC   = 'OP_INC'
MAX   = 'OP_MAX'
MIN   = 'OP_MIN'
RW    = 'OP_RW'
READ  = 'OP_READ'
WRITE = 'OP_WRITE'

DAT_ACCESS_TYPES = [READ, WRITE, RW, INC]
GBL_ACCESS_TYPES = [READ, INC, MAX, MIN]


class OpError(Exception):
  message: str
  # loc:

  def __init__(self, message: str, loc = None):
    self.message = message
    self.loc = loc

  def __str__(self) -> str:
    if self.loc:
      return f'{self.loc}: OP error: {self.message}'
    else:
      return f'OP error: {self.message}'


class Set:
  name: str

  def __init__(self, name: str):
    self.name = name


class Map:
  dim: int

  def __init__(self, dim: int):
    self.dim = dim
  

class Data:
  set: str
  dim: int
  typ: str

  def __init__(self, set_: str, dim: int, typ: str):
    self.set = set_
    self.dim = dim
    self.typ = typ


class Const:
  name: str
  dim: int
  # loc: 

  def __init__(self, name: str, dim: int, loc):
    self.name = name
    self.dim = dim
    self.loc = loc


class Arg:
  var: str
  dim: int
  typ: str
  acc: str
  # loc:
  map: str
  idx: int
  opt: Optional[str]

  def __init__(self, var: str, dim: int, typ: str, acc: str, loc, map_: str = None, idx: int = None):
    self.var = var
    self.dim = dim
    self.typ = typ
    self.acc = acc
    self.loc = loc
    self.map = map_
    self.idx = idx
    self.opt = None

    # TODO: 0 indexing for c, 1 indexing for f
    # if map_ == ID:
    #   if idx != -1:
    #     raise OpError('incompatible index for direct access, expected -1', loc)
    # elif map_ and idx is not None:
    #   if idx < 0 or idx >= dim:
    #     raise OpError(f'index out of range, must be in the interval [0,{dim-1}]', loc)


  @property
  def direct(self) -> bool:
    return self.map == ID


  @property
  def indirect(self) -> bool:
    return self.map is not None and self.map != ID


  @property
  def global_(self):
    return self.map is None 


class Loop:
  name: str
  set: str
  args: Dict[int, Arg] 
  # loc: 

  def __init__(self, kernel: str, set_: str, args: List[Arg], loc = None):
    self.name = kernel
    self.set = set_
    self.args = dict(enumerate(args))
    self.loc = loc


  @property
  def indirection(self):
    return len(self.indirects) > 0


  @property
  def directs(self):
    return { i: arg for i, arg in self.args.items() if arg.direct }


  @property
  def indirects(self):
    return { i: arg for i, arg in self.args.items() if arg.indirect }


  @property
  def globals(self):
    return { i: arg for i, arg in self.args.items() if arg.global_ }


  @property
  def indirectVars(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg.var
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMaps(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg.map
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMapRefs(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = (arg.map, arg.idx)
      if y not in x:
        x.append(y)
        r[i] = arg

    return r

