# Standard library imports
import subprocess


def getVersion() -> str:
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def enumRegex(values: [str]) -> str:
  return '(' + ')|('.join(values) + ')'


