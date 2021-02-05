
# Standard library imports
import re

# Application imports
from store import Store


# Augment source program to use generated kernel hosts
def translateProgram(source: str, store: Store, soa: bool = False) -> str:
  lines = source.splitlines(True)
  
  # 1. Update const calls
  for const in store.consts:
    lines[const.loc.line - 1] = re.sub(
      r'op_decl_const\s*\(',
      f'op_decl_const2("{const.debug}", ',
      lines[const.loc.line - 1]
    )

  # 2. Update loop calls
  for loop in store.loops:
    before, after = lines[loop.loc.line - 1].split('op_par_loop', 1)
    after = re.sub(f'{loop.kernel}\s*,\s*', '', after, count=1) # TODO: This assumes that the kernel arg is on the same line as the call
    lines[loop.loc.line - 1] = before + f'op_par_loop_{loop.name}_host' + after

  # 3. Update headers
  index = lines.index('#include "op_seq.h"\n') + 2 # TODO: Make more robust
  for loop in store.loops:
    prototype = f'void op_par_loop_{loop.name}_host(char const *, op_set{", op_arg" * len(loop.args)});\n'
    lines.insert(index, prototype)

  # 4. Update init call TODO: Use a line number from the store
  source = ''.join(lines)
  if soa:
    source = re.sub(r'\bop_init\b\s*\((.*)\)','op_init_soa(\\1,1)', source)
    source = re.sub(r'\bop_mpi_init\b\s*\((.*)\)','op_mpi_init_soa(\\1,1)', source)
  
  return source

