
class Lang:
  def __init__(self, name, extensions, com_delim):
    self.name = name
    self.extensions = extensions
    self.com_delim = com_delim

  def __str__(self):
      return self.name


langs = [
  Lang('C', 'c', '//'),
  Lang('Modern Fortran', ['F90', 'F95'], '!'),
]


def findLang(extension):
  return next((l for l in langs if extension in l.extensions), None)


def supportedExtensions():
  return [ ex for lang in langs for ex in lang.extensions ]


def isSupported(extension):
  return extension in supportedExtensions()

