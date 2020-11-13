

class Store:
  def __init__(self):
    self.init = None # TODO: Prevent multiple inits
    self.exit = False # TODO: Prevent multiple exits
    self.consts = []
    self.loops = []


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

    for const in store.consts:
      self.addConst(const)

    for loop in store.loops:
      self.addLoop(loop)


  def __str__(self):
    return f"{'init, ' if self.init else ''}{len(self.consts)} constants, {len(self.loops)} loops{' exit' if self.exit else ''}"

