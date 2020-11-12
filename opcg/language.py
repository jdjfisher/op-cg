
# Application imports
import parsers.fortran as fp

class Lang:
  def __init__(self, name, extensions, com_delim, parser):
    self.name = name
    self.extensions = extensions
    self.com_delim = com_delim
    self.parser = parser


  def parse(self, path):
    if not self.parser:
      raise Exception(f'f')

    return self.parser(path)


  def __str__(self):
      return self.name


langs = [
  Lang('C++', ['cpp'], '//', None),
  Lang('Fortran', ['F90', 'F95'], '!', fp.parse),
]


def findLang(extension):
  return next((l for l in langs if extension in l.extensions), None)


def supportedLangs():
  return [ lang.name for lang in langs ]


def supportedLangExts():
  return [ ex for lang in langs for ex in lang.extensions ]


