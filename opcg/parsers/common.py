

class Store:
  def __init__(self):
    self.init = None # TODO: Prevent multiple inits
    self.consts = []
    self.loops = []
    self.exit = None # TODO: Prevent multiple exits


  def recordInit(self, init):
    if self.init:
      raise Exception()
    else:
      self.init = init


  def addConst(self, const):
    # Search for previous decleration
    prev = next((c for c in self.consts if c['name'] == const['name']), None)

    # If there is a previous decleration verify compatibilty and then skip
    if prev:
      if const['type'] != prev['type']:
        raise Exception(f"type mismatch in repeated decleration of '{const['name']}' const")  
      elif const['dim'] != prev['dim']:
        raise Exception(f"size mismatch in repeated decleration of '{const['name']}' const") 
      else:
        return
      
    # Store const
    self.consts.append(const)


  def addLoop(self, loop):
    # TODO: Check for repeats / compatitbility 
    self.loops.append(loop)


  def merge(self, store):
    # TODO: Finish

    if store.init:
      self.recordInit(store.init)

    for const in store.consts:
      self.addConst(const)

    for loop in store.loops:
      self.addLoop(loop)

    if store.exit:
      self.recordExit(store.exit)


  def recordExit(self, exit):
    if self.exit:
      raise Exception()
    else:
      self.exit = exit


  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"


class ParseError(Exception):
  def __init__(self, message, location=None):
    self.message = message
    self.line = location['line_begin']
    self.col = location['col_begin']


  def __str__(self):
    return self.message