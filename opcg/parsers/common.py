# Standard library imports
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from typing_extensions import Protocol
from os.path import basename
from pathlib import Path

# Application imports
from op import OpError
from util import safeFind
import op as OP
if TYPE_CHECKING:
  from language import Lang


class Parser(Protocol):
  def __call__(self, path: Path) -> Store: ...


class Location:
  file: str
  line: int
  column: int
  
  def __init__(self, file: str, line: int, column: int) -> None:
    self.file = file
    self.line = line
    self.column = column


  def __str__(self) -> str:
    return f'{basename(self.file)}/{self.line}:{self.column}'


class ParseError(Exception):
  message: str
  loc: Optional[Location]

  def __init__(self, message: str, loc: Location = None) -> None:
    self.message = message
    self.loc = loc

  def __str__(self) -> str:
    if self.loc:
      return f'{self.loc}: parse error: {self.message}'
    else:
      return f'parse error: {self.message}'


class Store:
  init: Optional[Location]
  exit: bool
  sets: List[OP.Set]
  maps: List[OP.Map]
  datas: List[OP.Data]
  loops: List[OP.Loop]
  consts: List[OP.Const]


  def __init__(self) -> None:
    self.init = None 
    self.exit = False 
    self.sets = []
    self.maps = []
    self.datas = []
    self.loops = []
    self.consts = []


  def recordInit(self, loc) -> None:
    if self.init:
      exit('multiple calls to op_init')

    self.init = loc


  def recordExit(self) -> None:
    self.exit = True


  def addSet(self, set_: OP.Set) -> None:
    self.sets.append(set_)


  def addMap(self, map_: OP.Map) -> None:
    self.maps.append(map_)


  def addData(self, data: OP.Data) -> None:
    self.datas.append(data)


  def addConst(self, const: OP.Const) -> None:
    # Search for previous decleration
    prev = safeFind(self.consts, lambda c: c.ptr == const.ptr)

    # If there is a previous decleration verify compatibilty and then skip
    if prev:
      if const.dim != prev.dim:
        raise ParseError(f"dim mismatch in repeated decleration of '{const.ptr}' const")  
      
      elif const.dim != prev.dim:
        raise ParseError(f"size mismatch in repeated decleration of '{const.ptr}' const") 
      
      else:
        return # TODO: We need to keep track of the location still
      
    # Store const
    self.consts.append(const)


  def addLoop(self, loop: OP.Loop) -> None:
    # Search for previous decleration on the same kernel
    prev = safeFind(self.loops, lambda l: l.kernel == loop.kernel)

    if prev:
      # TODO: Check for compatitbile repeats (and then skip the loop but track its location)

      # Ensure the previous loop has an index
      if prev.i is None:
        prev.i = 1
        
      # Give the new loop a unqiue index
      loop.i = prev.i + 1

    self.loops.append(loop)


  def merge(self, store: Store) -> None:
    self.recordInit(store.init)

    if store.exit:
      self.recordExit()
    
    for s in store.sets:
      self.addSet(s)

    for m in store.maps:
      self.addMap(m)

    for d in store.datas:
      self.addData(d)

    for c in store.consts:
      self.addConst(c)

    for l in store.loops:
      self.addLoop(l)


  def validate(self, lang: Lang) -> None:
    if not self.init:
      print('OP warning: No call to op_init found')

    if not self.exit:
      print('OP warning: No call to op_exit found')

    # Collect the pointers of defined sets
    set_ptrs = [ s.ptr for s in self.sets ]

    # Validate data declerations
    for data in self.datas:
      # Validate set
      if data.set not in set_ptrs:
        raise OpError(f'undefined set "{data.set}" referenced in data decleration', data.loc)

      # Validate type
      if data.typ not in lang.types:
        raise OpError(f'unsupported datatype "{data.typ}" for the {lang.name} language', data.loc)

    # Validate map declerations
    for map in self.maps:
      # Validate both sets
      for set_ in (map.from_set, map.to_set):
        if set_ not in set_ptrs:
          raise OpError(f'undefined set "{set_}" referenced in map decleration', map.loc)

    # Validate loop calls
    for loop in self.loops:
      # Validate loop dataset
      if loop.set not in set_ptrs:
        raise OpError(f'undefined set "{loop.set}" referenced in par loop call', loop.loc)

      # Validate loop args
      for arg in loop.args:
        if not arg.global_:
          # Look for the referenced data
          data_ = safeFind(self.datas, lambda d: d.ptr == arg.var)

          # Validate the data referenced in the arg 
          if not data_:
            raise OpError(f'undefined data "{arg.var}" referenced in par loop arg', arg.loc)
          elif arg.typ != data_.typ:
            raise OpError(f'type mismatch of par loop data, expected {data_.typ}', arg.loc)
          elif arg.dim != data_.dim:
            raise OpError(f'dimension mismatch of par loop data, expected {data_.dim}', arg.loc)

          # Validate direct args
          if arg.direct:
            # Validate index
            if arg.idx != -1:
              raise OpError('incompatible index for direct access, expected -1', arg.loc)
            # Check the dataset can be accessed directly
            if data_.set != loop.set:
              raise OpError(f'cannot directly access the "{arg.var}" dataset from the "{loop.set}" loop set', arg.loc)

            # Check that the same dataset has not already been directly accessed
            if safeFind(loop.directs, lambda a: a is not arg and a.var == arg.var):
              raise OpError(f'duplicate direct accesses to the "{arg.var}" dataset in the same par loop', arg.loc)

          # Validate indirect args
          elif arg.indirect:
            # Look for the referenced map decleration
            map_ = safeFind(self.maps, lambda m: m.ptr == arg.map)

            if not map_:
              raise OpError(f'undefined map "{arg.map}" referenced in par loop arg', arg.loc)

            # Check that the mapping maps from the loop set
            if map_.from_set != loop.set:
              raise OpError(f'cannot apply the "{arg.map}" mapping to the "{loop.set}" loop set', arg.loc)

            # Check that the mapping maps to the data set
            if map_.to_set != data_.set:
              raise OpError(f'cannot map to the "{arg.var}" dataset with the "{arg.map}" mapping', arg.loc)

            # Determine the valid index range using the given language
            min_idx = 0 if lang.zero_idx else 1
            max_idx = map_.dim - 1 if lang.zero_idx else map_.dim

            # Perform range check
            if arg.idx is None or arg.idx < min_idx or arg.idx > max_idx:
              raise OpError(f'index {arg.idx} out of range, must be in the interval [{min_idx},{max_idx}]', arg.loc)

          # Enforce unique data access
          for other in loop.args:
            if other is not arg and other.var == arg.var and (other.idx == arg.idx and other.map == arg.map):
              raise OpError(f'duplicate data accesses in the same par loop', arg.loc)


  @property
  def kernels(self):
    return set([ loop.kernel for loop in self.loops ])


  def __str__(self) -> str:
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{', exit' if self.exit else ''}"


