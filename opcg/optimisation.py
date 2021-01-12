# Standard library imports
from __future__ import annotations # https://stackoverflow.com/questions/41135033/type-hinting-within-a-class


class Opt(object):
  instances: [Opt] = []

  def __init__(self, name: str):
    self.__class__.instances.append(self)
    self.name = name


  def __str__(self) -> str:
    return self.name


  @classmethod
  def all(cls) -> [Opt]:
    return cls.instances


  @classmethod
  def names(cls) -> [str]:
    return [ o.name for o in cls.all() ]


  @classmethod
  def find(cls, name: str) -> Opt:
    return next((o for o in cls.all() if o.name == name), None)


# 
seq  = Opt('seq'),
cuda = Opt('cuda'),
omp  = Opt('omp3'),



