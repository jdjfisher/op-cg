# Standard library imports
from __future__ import annotations # https://stackoverflow.com/questions/41135033/type-hinting-within-a-class
from typing import Callable, Optional, List

# Application imports
from parsers.common import Store, ParseError
import parsers.fortran as fp
import parsers.cpp as cp


class Lang(object):
  instances: List[Lang] = []

  def __init__(self, name: str, extensions: List[str], com_delim: str, parser: Callable[[str], Store]):
    self.__class__.instances.append(self)
    self.name = name
    self.extensions = extensions
    self.com_delim = com_delim
    self.parser = parser


  def parse(self, path: str) -> Store:
    if not self.parser:
      raise NotImplementedError(f'no parser registered for the "{self.name}" language')

    try:
      return self.parser(path)
    except ParseError as e:
      exit(e)


  def __str__(self) -> str:
      return self.name


  @classmethod
  def all(cls) -> List[Lang]:
    return cls.instances


  @classmethod
  def find(cls, name: str) -> Optional[Lang]:
    return next((l for l in cls.all() if name == l.name or name in l.extensions), None)



c = Lang('c++', ['cpp'], '//', cp.parse),
f = Lang('fortran', ['F90', 'F95'], '!', fp.parse),

