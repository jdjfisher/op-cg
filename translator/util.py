

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
