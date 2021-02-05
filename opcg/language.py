# Standard library imports
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, ClassVar, Set
from pathlib import Path

# Application imports
from parsers.store import Store, ParseError
import parsers.fortran as fp
import parsers.cpp as cp
from util import find


class Lang(object):
  instances: ClassVar[List[Lang]] = []

  name: str
  com_delim: str
  types: List[str]
  source_exts: List[str]
  include_ext: str
  zero_idx: bool


  def __init__(
    self, 
    name: str, 
    com_delim: str, 
    types: List[str], 
    source_exts: List[str], 
    include_ext: str, 
    zero_idx: bool = True
  ) -> None:
    self.__class__.instances.append(self)
    self.name = name
    self.com_delim = com_delim
    self.types = types
    self.source_exts = source_exts
    self.include_ext = include_ext
    self.zero_idx = zero_idx


  def parseProgram(self, path: Path, include_dirs: Set[Path]) -> Store:
    raise NotImplementedError(f'no program parser registered for the "{self.name}" language')


  def parseKernel(self, path: Path, kernel: str) -> List[str]:
    raise NotImplementedError(f'no kernel parser registered for the "{self.name}" language')


  def __str__(self) -> str:
      return self.name


  def __eq__(self, other) -> bool:
    return self.name == other.name if type(other) is type(self) else False


  def __hash__(self) -> int:
    return hash(self.name)


  @classmethod
  def all(cls) -> List[Lang]:
    return cls.instances


  @classmethod
  def find(cls, name: str) -> Lang:
    return find(cls.all(), lambda l: name == l.name or name in l.source_exts)



# Define languages here ...

c = Lang(
  name='c++', 
  com_delim='//', 
  source_exts=['cpp'], 
  include_ext='h',
  types=['float', 'double', 'int', 'uint', 'll', 'ull', 'bool'], 
)

f = Lang(
  name='fortran', 
  com_delim='!',
  zero_idx=False, 
  source_exts=['F90', 'F95'], 
  include_ext='inc',
  types=['integer(4)', 'real(8)'],
)

# Register parsers ...

setattr(c, 'parseProgram', cp.parseProgram)
setattr(c, 'parseKernel', cp.parseKernel)

setattr(f, 'parseProgram', fp.parseProgram)
setattr(f, 'parseKernel', fp.parseKernel)



