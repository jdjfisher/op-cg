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


class Kernel:

  def __init__(self, id, loop):
    self.id = id
    self.name = loop['kernel']
    self._args = loop['args']


  @property
  def args(self):
    return dict(enumerate(self._args))


  @property
  def indirection(self):
    return len(self.indirects) > 0


  @property
  def directs(self):
    return { i: arg for i, arg in self.args.items() if arg.get('map') == 'OP_ID' }


  @property
  def indirects(self):
    return { i: arg for i, arg in self.args.items() if 'map' in arg and arg.get('map') != 'OP_ID' }


  @property
  def globals(self):
    return { i: arg for i, arg in self.args.items() if 'map' not in arg }


  @property
  def indirectVars(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg['var']
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMaps(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg['map']
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMapRefs(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = (arg['map'], arg['idx'])
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


class Store:
  def __init__(self):
    self.init = False 
    self.exit = False 
    self.sets = []
    self.maps = []
    self.datas = []
    self.consts = []
    self.loops = []


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


  def addLoop(self, loop):
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
    return [ Kernel(i, loop) for i, loop in enumerate(self.loops) ]


  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"


