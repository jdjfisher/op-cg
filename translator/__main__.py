#!/usr/bin/python


# Standard library imports
import subprocess
import argparse
import os
import re 


# Program entrypoint
def main(argv=None):

  # Build arg parser
  parser = argparse.ArgumentParser()
  parser.add_argument('-version', '--version', help='Version', action='version', version=getVersion())
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('-p', '--prefix', help='Output File Prefix', type=isValidPrefix, default='op_')
  parser.add_argument('files', help='Input Files', type=isFilePath, nargs='+')
  args = parser.parse_args(argv)

  # TODO: Check file extensions are a supported langauge. Also deal with varying supported extensions.

  # Process the input files
  n = len(args.files)
  for i, raw_file in enumerate(args.files, 1):

    if args.verbose:
      print(f'Processing file {i} of {n}: {raw_file}')
    
    # Read the source file
    with open(raw_file, 'r') as raw_data:

      # Do some stuff ..
      data = raw_data.read()

      # Form output file path 
      new_file = os.path.join(args.out, args.prefix + os.path.basename(raw_file))

      # Write the source file
      with open(new_file, 'w') as new_data:
        new_data.write(data)


  # End of main
  exit()


def getVersion():
  return 'Unknown'


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


def isValidPrefix(prefix):
  if re.compile(r"^[a-zA-Z0-9_-]+$").match(prefix):
    return prefix
  else:
    raise argparse.ArgumentTypeError(f"invalid output file prefix: {prefix}")


if __name__ == '__main__':
  main()