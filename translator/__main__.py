#!/usr/bin/python

# Standard library imports
import argparse


def main(argv=None):
  parser = argparse.ArgumentParser(prog='translator')
  parser.add_argument('-version', '--version', help='Version', action='store_true')
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  args = parser.parse_args(argv)

  if args.version:
    print('0.0.0')
    exit()

  print('Hello world!')


if __name__ == '__main__':
  main()