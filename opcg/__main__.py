#!/usr/bin/python

# Standard library imports
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from datetime import datetime
from pathlib import Path
from typing import List
import json
import os
import re 

# Application imports
from generator import genLoopHost, genMakefile
from store import Store, ParseError
from util import getVersion, safeFind
from optimisation import Opt
from language import Lang



# Program entrypoint
def main(argv=None) -> None:
  # Build arg parser
  parser = ArgumentParser(prog='opcg')

  # Flags
  parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=getVersion())
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-d', '--dump', help='Dump Store', action='store_true')
  parser.add_argument('-m', '--makefile', help='Create Makefile', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('-p', '--prefix', help='Output File Prefix', type=isValidPrefix, default='op')
  parser.add_argument('-soa', '--soa', help='Structs of Arrays', action='store_true')
  parser.add_argument('-I', help='Header Include', type=isDirPath, action='append', nargs='+', default=['.'])
  
  # Positional args
  parser.add_argument('optimisation', help='Target Optimisation', type=str, choices=Opt.names())
  parser.add_argument('file_paths', help='Input Files', type=isFilePath, nargs='+')

  # Invoke arg parser
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

  # Parsing phase
  stores, heap_store = parsing(args, lang)

  # Code-generation phase
  codegen(args, lang, opt, stores, heap_store)

  # End of main
  if args.verbose:
    print('\nTerminating')



def parsing(args: Namespace, lang: Lang):
  # Collect the include directories
  include_dirs = set([ Path(dir) for [ dir ] in args.I ])

  stores = []

  # Parse the input files
  for i, raw_path in enumerate(args.file_paths, 1):

    if args.verbose:
      print(f'Parsing file {i} of {len(args.file_paths)}: {raw_path}')
    
    # Create a store
    store = lang.parseProgram(Path(raw_path), include_dirs) 
    stores.append(store)

    if args.verbose:
      print(f'  Parsed: {store}')

  # Fold all the parsed stores into one
  heap_store = Store()
  for store in stores:
    heap_store.merge(store)

  # Run semantic checks on the store content
  heap_store.validate(lang)

  # 
  for kernel in heap_store.kernels:
    # Locate kernel header file
    file_name = f'{kernel}.{lang.include_ext}'
    include_paths = [ os.path.join(dir, file_name) for dir in include_dirs ]
    kernel_path = safeFind(include_paths, os.path.isfile)
    if not kernel_path:
      exit(f'failed to locate kernel include {file_name}')

    # Parse kernel header file
    param_types = lang.parseKernel(Path(kernel_path), kernel)

    # Validate par loop arguments against kernel parameters
    for loop in heap_store.loops:
      if loop.kernel == kernel:
        if len(param_types) != len(loop.args):
          raise ParseError(f'incorrect number of args passed to the {kernel} kernel', loop.loc)
          
        for i, (param_type, arg) in enumerate(zip(param_types, loop.args)):
          if arg.typ != param_type:
            raise ParseError(f'argument {i} to {kernel} kernel has incompatible type {arg.typ}, expected {param_type}', arg.loc)

  # Dump heap store to a json file
  if args.dump:
    store_path = os.path.join(args.out, 'store.json')

    with open(store_path, 'w') as file:
      file.write(json.dumps(heap_store.__dict__, default=vars, indent=4))

    if args.verbose:
      print('Dumped store:', store_path, end='\n\n')

  return stores, heap_store



def codegen(args: Namespace, lang: Lang, opt: Opt, stores: List[Store], heap_store: Store):
  # Collect the paths of the generated files
  generated_paths: List[Path] = []

  # Generate loop optimisations
  for i, loop in enumerate(heap_store.loops, 1):

    # Generate loop host source
    source, extension = genLoopHost(lang, opt, loop, i)

    # Form output file path 
    path = Path(os.path.join(args.out, f'{args.prefix}_{opt.name}_{loop.name}.{extension}'))

    # Write the generated source file
    with open(path, 'w') as file:
      file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by opcg\n\n')
      file.write(source)
      generated_paths.append(path)

      if args.verbose:
        print(f'Generated loop host {i} of {len(heap_store.loops)}: {path}')

  # Generate program translations
  for i, (raw_path, store) in enumerate(zip(args.file_paths, stores), 1):

    # Read the raw source file
    with open(raw_path, 'r') as raw_file:

      # Generate the translated source
      source = lang.translateProgram(raw_file.read(), store, args.soa)

      # Form output file path 
      new_path = Path(os.path.join(args.out, f'{args.prefix}_{os.path.basename(raw_path)}'))

      # Write the translated source file
      with open(new_path, 'w') as new_file:
        new_file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by opcg\n\n')
        new_file.write(source)
        generated_paths.append(new_path)

        if args.verbose:
          print(f'Translated program  {i} of {len(args.file_paths)}: {new_path}') 

  # Generate Makefile
  if args.makefile:
    # TODO: Append directive if file exists
    with open(os.path.join(args.out, 'Makefile'), 'w') as file:

      source = genMakefile(opt, generated_paths)
      
      file.write(f'\n# Auto-generated at {datetime.now()} by opcg\n\n')
      file.write(source)
      
      if args.verbose:
        print(f'Created Makefile') 



def isDirPath(path):
  if os.path.isdir(path):
    return path
  else:
    raise ArgumentTypeError(f"invalid dir path: {path}")


def isFilePath(path):
  if os.path.isfile(path):
    return path
  else:
    raise ArgumentTypeError(f"invalid file path: {path}")


def isValidPrefix(prefix):
  if re.compile(r"^[a-zA-Z0-9_-]+$").match(prefix):
    return prefix
  else:
    raise ArgumentTypeError(f"invalid output file prefix: {prefix}")


if __name__ == '__main__':
  main()