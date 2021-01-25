#!/usr/bin/python

# Standard library imports
from datetime import datetime
from pathlib import Path
from typing import List
import argparse
import json
import os
import re 

# Application imports
from generator import genOpProgram, genLoopHost, genMakefile
from language import Lang
from optimisation import Opt
from parsers.common import Store
from util import getVersion


# Program entrypoint
def main(argv=None) -> None:
  # Build arg parser
  parser = argparse.ArgumentParser(prog='opcg')
  parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=getVersion())
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-d', '--dump', help='Dump Store', action='store_true')
  parser.add_argument('-m', '--makefile', help='Create Makefile', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('-p', '--prefix', help='Output File Prefix', type=isValidPrefix, default='op')
  parser.add_argument('-soa', '--soa', help='Structs of Arrays', action='store_true')
  parser.add_argument('optimisation', help='Target Optimisation', type=str, choices=Opt.names())
  parser.add_argument('file_paths', help='Input Files', type=isFilePath, nargs='+')
  args = parser.parse_args(argv)

  # Collect the set of file extensions
  extensions = { os.path.splitext(path)[1][1:] for path in args.file_paths }

  # Validate the file extensions
  if not extensions:
    exit('Missing file extensions, unable to determine target language.')

  elif len(extensions) > 1:
    exit('Varying file extensions, unable to determine target language.')

  else:
    [ extension ] = extensions 

  # Determine the target language and optimisation
  opt = Opt.find(args.optimisation)
  lang = Lang.find(extension)

  if not lang:
    exit(f'Unsupported file extension: {extension}')

  if args.verbose:
    print(f'Target language: {lang}')
    print(f'Target optimisation: {opt}\n')




  # ---                   Source Parsing                    --- #



  stores = []

  # Parse the input files
  for i, raw_path in enumerate(args.file_paths, 1):

    if args.verbose:
      print(f'Parsing file {i} of {len(args.file_paths)}: {raw_path}')
    
    # Create a store
    store = lang.parse(Path(raw_path)) 
    stores.append(store)

    if args.verbose:
      print(f'  Parsed: {store}')

  # Fold all the parsed stores into one
  main_store = Store()
  for store in stores:
    main_store.merge(store)

  # Run semantic checks on the store content
  main_store.validate(lang)

  if args.verbose:
    print('\nOP Store:', main_store)

  if args.dump:
    # Dump main store to a json file
    store_path = os.path.join(args.out, 'store.json')

    with open(store_path, 'w') as file:
      file.write(json.dumps(main_store.__dict__, default=vars, indent=4))
    if args.verbose:
      print('Dumped OP store:', store_path, end='\n\n')




  # ---                   Code generation                    --- #




  # Collect the paths of the generated files
  generated_paths: List[Path] = []

  # Generate loop optimisations
  for i, loop in enumerate(main_store.loops, 1):

    # Form output file path 
    path = Path(os.path.join(args.out, f'{args.prefix}_{opt.name}_{loop.name}.{extension}'))

    # Generate loop host source
    source = genLoopHost(lang, opt, loop, i)

    # Write the generated source file
    with open(path, 'w') as file:
      file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by {parser.prog}\n\n')
      file.write(source)
      generated_paths.append(path)

      if args.verbose:
        print(f'Generated loop host {i} of {len(main_store.loops)}: {path}')



  # Generate program translations
  for i, (raw_path, store) in enumerate(zip(args.file_paths, stores), 1):

    # Read the raw source file
    with open(raw_path, 'r') as raw_file:

      # Generate the translated source
      source = genOpProgram(lang, raw_file.read(), store, args.soa)

      # Form output file path 
      new_path = Path(os.path.join(args.out, f'{args.prefix}_{os.path.basename(raw_path)}'))

      # Write the translated source file
      with open(new_path, 'w') as new_file:
        new_file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by {parser.prog}\n\n')
        new_file.write(source)
        generated_paths.append(new_path)

        if args.verbose:
          print(f'Translated program  {i} of {len(args.file_paths)}: {new_path}') 




  # Generate Makefile
  if args.makefile:
    # TODO: Append directive if file exists
    with open(os.path.join(args.out, 'Makefile'), 'w') as file:

      source = genMakefile(opt, generated_paths)
      
      file.write(f'\n# Auto-generated at {datetime.now()} by {parser.prog}\n\n')
      file.write(source)
      
      if args.verbose:
        print(f'Created Makefile') 




  # End of main
  if args.verbose:
    print('\nTerminating')



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