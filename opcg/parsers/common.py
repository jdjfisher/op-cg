# Standard library imports
from __future__ import annotations
from os.path import basename
from typing import List

# Application imports
import op as OP


class ParseError(Exception):
  message: str
  # loc:

  def __init__(self, message: str, loc = None):
    self.message = message
    self.loc = loc

  def __str__(self) -> str:
    if self.loc:
      return f'{self.loc}: parse error: {self.message}'
    else:
      return f'parse error: {self.message}'


class Location:
  file: str
  line: int
  column: int
  
  def __init__(self, file: str, line: int, column: int):
    self.file = file
    self.line = line
    self.column = column


  def __str__(self) -> str:
    return f'{basename(self.file)}/{self.line}:{self.column}'


class Store:
  # init: 
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
    prev = next((c for c in self.consts if c.name == const.name), None)

    # If there is a previous decleration verify compatibilty and then skip
    if prev:
      if const.dim != prev.dim:
        raise ParseError(f"dim mismatch in repeated decleration of '{const.name}' const")  
      
      elif const.dim != prev.dim:
        raise ParseError(f"size mismatch in repeated decleration of '{const.name}' const") 
      
      else:
        return
      
    # Store const
    self.consts.append(const)


  def addLoop(self, loop: OP.Loop) -> None:
    # TODO: Check for repeats / compatitbility 
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


  def __str__(self) -> str:
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{', exit' if self.exit else ''}"


