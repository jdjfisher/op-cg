

class Para:
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name


paras = [
  Para('seq'),
  Para('cuda'),
  Para('omp3'),
  # ...
]


def findPara(name):
  return next(para for para in paras if para.name == name)


def supportedParas():
  return [ para.name for para in paras ]

