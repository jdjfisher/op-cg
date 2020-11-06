
class Lang:
  def __init__(self, name, extensions, com_delim):
    self.name = name
    self.extensions = extensions
    self.com_delim = com_delim

  def __str__(self):
      return self.name


langs = [
  Lang('C', 'c', '//'),
  Lang('Fortran', ['F90', 'F95'], '!'),
]


def findLang(extension):
  return next((l for l in langs if extension in l.extensions), None)


def supportedLangs():
  return [ lang.name for lang in langs ]


def supportedLangExts():
  return [ ex for lang in langs for ex in lang.extensions ]


