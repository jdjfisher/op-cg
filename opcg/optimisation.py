

#
class Opt(object):
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
    return [ o.name for o in cls.all() ]


  @classmethod
  def find(cls, name):
    return next((o for o in cls.all() if o.name == name), None)


# 
seq  = Opt('seq'),
cuda = Opt('cuda'),
omp  = Opt('omp3'),



