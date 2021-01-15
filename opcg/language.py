# Standard library imports
from __future__ import annotations
from typing import Callable, List

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


# Define languages here
c = Lang('c++', ['cpp'], '//', cp.parse)
f = Lang('fortran', ['F90', 'F95'], '!', fp.parse)

