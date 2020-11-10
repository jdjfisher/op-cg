

# TODO: Store refs to transaltion functions for lang, para pairings
schemes = {
  (1,2) : 3
}


class Transaltion:
  pass


def augmentProgram(source, store):
  # Augment source program to use generated parrallelisations
  # 1. Update headers
  # 2. Update init call
  # 3. Remove const calls
  # 4. Update loop calls
  return source


def genKernelHost(kernel, scheme):
  # Do lots of stuff ...

  source = ''

  return source