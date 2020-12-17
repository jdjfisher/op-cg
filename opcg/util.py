# Standard library imports
import subprocess


def getVersion():
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def enumRegex(values):
  return '(' + ')|('.join(values) + ')'


