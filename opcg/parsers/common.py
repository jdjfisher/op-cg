# Standard library imports
from os.path import basename

# Application imports
import op as OP


class ParseError(Exception):

  def __init__(self, message, location=None):
    self.message = message
    self.location = location

  def __str__(self):
    if self.location:
      return f'{self.location}: parse error: {self.message}'
    else:
      return f'parse error: {self.message}'


class Location:
  
  def __init__(self, file: str, line: int, column: int):
    self.file = file
    self.line = line
    self.column = column

  def __str__(self):
    return f'{basename(self.file)}/{self.line}:{self.column}'


class Store:
  init: bool
  exit: bool
  sets: [OP.Set]
  maps: [OP.Map]
  datas: [OP.Data]
  loops: [OP.Loop]
  consts: [OP.Const]


  def __init__(self):
    self.init = False 
    self.exit = False 
    self.sets = []
    self.maps = []
    self.datas = []
    self.loops = []
    self.consts = []


  def recordInit(self):
    self.init = True


  def recordExit(self):
    self.exit = True


  def addSet(self, set_: OP.Set):
    self.sets.append(set_)


  def addMap(self, map_: OP.Map):
    self.maps.append(map_)


  def addData(self, data: OP.Data):
    self.datas.append(data)


  def addConst(self, const: OP.Const):
    # Search for previous decleration
    prev = next((c for c in self.consts if c.name == const.name), None)

    # If there is a previous decleration verify compatibilty and then skip
    if prev:
      if const.dim != prev.dim:
        raise ParseError(f"dim mismatch in repeated decleration of '{const['name']}' const")  
      
      elif const.dim != prev.dim:
        raise ParseError(f"size mismatch in repeated decleration of '{const['name']}' const") 
      
      else:
        # prev.locations += const.locations
        return
      
    # Store const
    self.consts.append(const)


  def addLoop(self, loop: OP.Loop):
    # TODO: Check for repeats / compatitbility 
    self.loops.append(loop)
  

  def merge(self, store):
    map(self.addSet, store.sets)
    map(self.addMap, store.maps)
    map(self.addData, store.datas)
    map(self.addConst, store.consts)
    map(self.addLoop, store.loops)

    if store.init:
      self.recordInit()

    if store.exit:
      self.recordExit()


  def getKernels(self): 
    return self.loops


  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"


