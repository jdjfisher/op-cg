#!/usr/bin/python

# Standard library imports
import argparse
import os


# Program entrypoint
def main(argv=None):
  # Build arg parser
  parser = argparse.ArgumentParser(prog='translator')
  parser.add_argument('-version', '--version', help='Version', action='store_true')
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('in', help='Input Files', type=isFilePath, nargs='+')
  args = parser.parse_args(argv)

  # Dump version number
  if args.version:
    print('v0.0.0')
    exit()

  # ...
  print(args)
  exit()


def isDirPath(path):
  if os.path.isdir(path):
    return path
  else:
    raise argparse.ArgumentTypeError(f"invalid dir path: {path}")


def isFilePath(path):
  if os.path.isfile(path):
    return path
  else:
    raise argparse.ArgumentTypeError(f"invalid file path: {path}")


if __name__ == '__main__':
  main()