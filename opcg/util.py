
# Standard library imports
import os
import contextlib


def enumRegex(values):
  return '(' + ')|('.join(values) + ')'


def replaceCode(source, snip, lb, cb=0, le=None, ce=None):
  return source


# def silent(action):
#   with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
#     action()
