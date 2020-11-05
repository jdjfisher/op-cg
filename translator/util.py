
def extractDelimStr(text, delims, start=None):
  # Unpack
  left, right = delims

  i = start = text.find(left, start) + 1
  depth = 1

  # Scan the text until the same depth delimeter is found 
  while depth:
    if text[i] == left:
      depth += 1
    elif text[i] == right:
      depth -= 1
    i += 1
  else:
    end = i - 1

  return text[start:end]


def splitDelimStr(s):
     parts = []
     bracket_level = 0
     current = []
     # trick to remove special-case of trailing chars
     for c in (s + ","):
         if c == "," and bracket_level == 0:
             parts.append("".join(current))
             current = []
         else:
             if c == "{":
                 bracket_level += 1
             elif c == "}":
                 bracket_level -= 1
             current.append(c)
     return parts


# def pre():
#   compiler_path = 'gfortran'
#   sources = ['examples/airfoil/op2_for_declarations.F90', './examples/airfoil/airfoil.F90']
#   return_code = call([compiler_path] + sources, shell=True)  
#   print(return_code)
