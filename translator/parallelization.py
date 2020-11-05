

class Para:
  def __init__(self, name, file_prefix=None):
    self.name = name
    self.file_prefix = file_prefix or name.lower().replace(' ', '-')

  def __str__(self):
      return self.name


paras = [
  Para('cuda'),
  Para('omp3'),
  Para('omp4'),
  # ...
]


def findPara(name):
  return next(para for para in paras if para.name == name)


def supportedParas():
  return [ para.name for para in paras ]

