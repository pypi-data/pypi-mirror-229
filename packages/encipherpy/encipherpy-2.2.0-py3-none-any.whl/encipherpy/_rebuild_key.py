def _rebuildKey(plainText, key):
  targetLength = len(plainText)
  keyBoundary = (len(key) - 1)

  newKey = []

  keyPosition = 0
  for i in range(0, targetLength):
    if plainText[i] == " ":
      keyToAdd = " "
    elif plainText[i] == "#": # check for punctuation placeholders
      keyToAdd = "#"
    else:
      keyToAdd = key[keyPosition]
      if keyPosition == keyBoundary:
        keyPosition = 0
      else:
        keyPosition += 1
    newKey.append(keyToAdd)
  return "".join(newKey)