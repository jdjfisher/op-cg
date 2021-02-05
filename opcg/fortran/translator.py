
# Standard library imports
import re

# Application imports
from store import Store


# Augment source program to use generated kernel hosts
def translateProgram(source: str, store: Store, soa: bool = False) -> str:
  lines = source.splitlines(True)

  # 1. Comment-out const calls
  for const in store.consts:
    lines[const.loc.line - 1] = '! ' + lines[const.loc.line - 1]

  # 2. Update loop calls
  for loop in store.loops:
    before, after = re.split(r'op_par_loop_[1-9]\d*', lines[loop.loc.line - 1], 1)
    after = after.replace(loop.kernel, f'"{loop.kernel}"') # TODO: This assumes that the kernel arg is on the same line as the call
    lines[loop.loc.line - 1] = before + f'op_par_loop_{loop.name}_host' + after

  # 3. Update headers
  index = lines.index('  use OP2_Fortran_Reference\n')  # TODO: Make more robust
  for loop in store.loops:
    lines.insert(index, f'  use {loop.name.upper()}_MODULE\n') 

  # 4. Update init call TODO: Use a line number from the store
  source = ''.join(lines)
  if soa:
    source = re.sub(r'\bop_init(\w*)\b\s*\((.*)\)','op_init\\1_soa(\\2,1)', source)
    source = re.sub(r'\bop_mpi_init(\w*)\b\s*\((.*)\)','op_mpi_init\\1_soa(\\2,1)', source)

  return source


