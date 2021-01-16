# Standard library imports
from __future__ import annotations
from typing import List, ClassVar

# Application imports
from util import find

class Opt(object):
  instances: ClassVar[List[Opt]] = []

  def __init__(self, name: str) -> None:
    self.__class__.instances.append(self)
    self.name = name


  def __str__(self) -> str:
    return self.name


  def __eq__(self, other) -> bool:
    return self.name == other.name if isinstance(other, Opt) else False


  def __hash__(self) -> int:
    return hash(self.name)


  @classmethod
  def all(cls) -> List[Opt]:
    return cls.instances


  @classmethod
  def names(cls) -> List[str]:
    return [ o.name for o in cls.all() ]


  @classmethod
  def find(cls, name: str) -> Opt:
    return find(cls.all(), lambda o: o.name == name)


# Define optimisations here
seq  = Opt('seq')
cuda = Opt('cuda')
omp  = Opt('omp3')



