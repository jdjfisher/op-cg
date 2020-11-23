
# Standard library imports
from os.path import basename

# Application imports
from parsers.common import ParseError
import parsers.fortran as fp


class Lang(object):
  instances = []

  def __init__(self, name, extensions, com_delim, parser):
    self.__class__.instances.append(self)
    self.name = name
    self.extensions = extensions
    self.com_delim = com_delim
    self.parser = parser


  def parse(self, path):
    if not self.parser:
      raise NotImplementedError(f'no parser registered for the "{self.name}" language')

    try:
      return self.parser(path)
    except ParseError as e:
      exit(f'{basename(path)}:{e.line}:{e.col}: parse error: {e.message}')


  def __str__(self):
      return self.name


  @classmethod
  def all(cls):
    return cls.instances


  @classmethod
  def find(cls, name):
    return next((l for l in cls.all() if name == l.name or name in l.extensions), None)



c = Lang('c++', ['cpp'], '//', None),
f = Lang('fortran', ['F90', 'F95'], '!', fp.parse),

