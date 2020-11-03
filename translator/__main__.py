#!/usr/bin/python

# Standard library imports
from datetime import datetime
import subprocess
import argparse
import os
import re 

# Application imports
from translator import translateProgram
from language import isSupported, findLang
from parallelization import findPara


# Program entrypoint
def main(argv=None):

  # Build arg parser
  parser = argparse.ArgumentParser(prog='w.i.p')
  parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=getVersion())
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('-p', '--prefix', help='Output File Prefix', type=isValidPrefix, default='op_')
  parser.add_argument('file_paths', help='Input Files', type=isFilePath, nargs='+')
  args = parser.parse_args(argv)

  # Collect the set of file extensions
  extensions = { os.path.splitext(path)[1][1:] for path in args.file_paths }

  # Validate the file extensions
  if not extensions:
    raise Exception('Missing file extensions, unable to determine target language.')

  elif len(extensions) > 1:
    raise Exception('Varying file extensions, unable to determine target language.')

  else:
    [ extension ] = extensions 
    if not isSupported(extension):
      raise Exception(f'Unsupported file extension: {extension}')

  # Determine the target language and translation
  l = findLang(extension)
  p = findPara()

  if args.verbose:
    print(f'Target language: {l}')
    print(f'Target parallelization: {p}')

  # Process the files
  for i, raw_path in enumerate(args.file_paths, 1):

    if args.verbose:
      print(f'Processing file {i} of {len(args.file_paths)}: {raw_path}')
    
    # Read the raw source file
    with open(raw_path, 'r') as raw_file:

      # Translate the source
      translation = translateProgram(raw_file.read())

      # Form output file path 
      new_path = os.path.join(args.out, args.prefix + os.path.basename(raw_path))

      # Write the new source file
      with open(new_path, 'w') as new_file:
         
        new_file.write(f'\n{l.com_delim} Auto-generated at {datetime.now()} by {parser.prog}\n\n')
        new_file.write(translation)

        if args.verbose:
          print(f'  Created translation file: {new_path}')

  if args.verbose:
    print('Done')


def getVersion():
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


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