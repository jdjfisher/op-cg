# Standard library imports
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, ClassVar

# Application imports
from parsers.common import Store, ParseError
import parsers.fortran as fp
import parsers.cpp as cp


class Lang(object):
  instances: ClassVar[List[Lang]] = []

  name: str
  com_delim: str
  types: List[str]
  extensions: List[str]
  parser: Callable[[str], Store]
  zero_idx: bool


  def __init__(
    self, 
    name: str, 
    com_delim: str, 
    types: List[str], 
    extensions: List[str], 
    parser: Callable[[str], Store],
    zero_idx: bool = True
  ):
    self.__class__.instances.append(self)
    self.name = name
    self.com_delim = com_delim
    self.types = types
    self.extensions = extensions
    self.parser = parser
    self.zero_idx = zero_idx


  def parse(self, path: str) -> Store:
    if not self.parser:
      raise NotImplementedError(f'no parser registered for the "{self.name}" language')

    try:
      return self.parser(path)
    except Exception as e:
      exit(e)


  def __str__(self) -> str:
      return self.name


  def __eq__(self, other) -> bool:
    return self.name == other.name if isinstance(other, Lang) else False


  def __hash__(self) -> int:
    return hash(self.name)


  @classmethod
  def all(cls) -> List[Lang]:
    return cls.instances


  @classmethod
  def find(cls, name: str) -> Lang:
    return next((l for l in cls.all() if name == l.name or name in l.extensions))



# Define languages here ...

c = Lang(
  name='c++', 
  parser=cp.parse,
  com_delim='//', 
  extensions=['cpp'], 
  types=['float', 'double', 'int', 'uint', 'll', 'ull', 'bool'], 
)

f = Lang(
  name='fortran', 
  parser=fp.parse,
  com_delim='!',
  zero_idx=False, 
  extensions=['F90', 'F95'], 
  types=['integer(4)', 'real(8)'], # TODO: Check these
)

