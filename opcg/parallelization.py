

#
class Para(object):
  instances = []

  def __init__(self, name):
    self.__class__.instances.append(self)
    self.name = name


  def __str__(self):
    return self.name


  @classmethod
  def all(cls):
    return cls.instances


  @classmethod
  def names(cls):
    return [ p.name for p in cls.all() ]


  @classmethod
  def find(cls, name):
    return next((p for p in cls.all() if p.name == name), None)


# 
seq  = Para('seq'),
cuda = Para('cuda'),
omp  = Para('omp3'),



