# Standard library imports
from typing import TypeVar, Callable, Generic, Optional, Iterable, List
import subprocess
import re


# Generic type
T = TypeVar('T')


def getVersion() -> str:
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def enumRegex(values: List[str]) -> str:
  return '(' + ')|('.join(map(re.escape, values)) + ')'


def find(xs: Iterable[T], p: Callable[[T], bool]) -> T:
  return next(x for x in xs if p(x))


def safeFind(xs: Iterable[T], p: Callable[[T], bool]) -> Optional[T]:
  return next(( x for x in xs if p(x) ), None)
