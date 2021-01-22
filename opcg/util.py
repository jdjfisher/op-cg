# Standard library imports
from typing import TypeVar, Callable, Generic, Optional, Iterable, List, Any, Set
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


def uniqueBy(xs: Iterable[T], f: Callable[[T], Any]) -> List[T]:
  s, u = set(), list()
  for x in xs:
    y = f(x)
    if y not in s:
      s.add(y)
      u.append(x)

  return u
