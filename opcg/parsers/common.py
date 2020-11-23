

class Store:
  def __init__(self):
    self.init = None 
    self.consts = []
    self.loops = []
    self.exit = None 


  def recordInit(self, init):
    if self.init:
      raise ParseError('multiple calls to op_init')
    else:
      self.init = init


  def addConst(self, const):
    # Search for previous decleration
    prev = next((c for c in self.consts if c['name'] == const['name']), None)

    # If there is a previous decleration verify compatibilty and then skip
    if prev:
      if const['dim'] != prev['dim']:
        raise ParseError(f"dim mismatch in repeated decleration of '{const['name']}' const")  
      elif const['dim'] != prev['dim']:
        raise ParseError(f"size mismatch in repeated decleration of '{const['name']}' const") 
      else:
        prev['locations'] += const['locations']
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


  def getKernels(self): # WIP
    kernels = []

    for loop in self.loops:

      # TODO: Identify indirect accesses
      # j = [i for i, arg in enumerate(loop['args']) if 'map' in arg and arg['map'] != 'OP_ID']
      # ninds = 0

      # for arg in loop['args'] if 'map' in arg and arg['map'] != 'OP_ID':
      #   pass

      kernels.append({
        'name': loop['kernel'],
        'set': loop['set'],
      })

    return kernels


  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"


class ParseError(Exception):
  def __init__(self, message, location=None):
    self.message = message
    self.line = location['line_begin'] if location else '?'
    self.col = location['col_begin'] if location else '?'


  def __str__(self):
    return self.message