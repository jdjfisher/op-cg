# Standard library imports
from typing import List
import subprocess


def getVersion() -> str:
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def enumRegex(values: List[str]) -> str:
  return '(' + ')|('.join(values) + ')'


