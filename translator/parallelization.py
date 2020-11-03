

class Para:
  def __init__(self, name):
    self.name = name

  def __str__(self):
      return self.name


parallelizations = [
  Para('Cuda'),
  Para('Omp3'),
]


def findPara():
  return '...'

