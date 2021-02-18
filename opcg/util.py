# Standard library imports
from typing import TypeVar, Callable, Generic, Optional, Iterable, List, Any, Set, Tuple
from pathlib import Path
import subprocess
import re


# Generic type
T = TypeVar('T')


def getRootPath() -> Path:
  return Path(__file__).parent.parent.absolute()


def getVersion() -> str:
  args = ['git', '-C', str(getRootPath()), 'describe', '--always']
  return subprocess.check_output(args).strip().decode()


def enumRegex(values: List[str]) -> str:
  return '(' + ')|('.join(map(re.escape, values)) + ')'


def indexSplit(s: str, i: int) -> Tuple[str, str]:
  if i >= len(s):
    return s, '' 
  elif i <= -len(s):
    return '', s 
  else:
    return s[:i], s[i:]


def flattern(arr: List[List[T]]) -> List[T]:
  return sum(arr, [])


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
