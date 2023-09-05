def rot47(plainText):
  alphabet = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

  cipherText = []

  for character in plainText:
    if character == " ":
      cipherText.append(" ")
    else:
      index = alphabet.find(character)
      shiftedIndex = (index + 47) % 94
      cipherCharacter = alphabet[shiftedIndex]
      cipherText.append(cipherCharacter)

  cipherText = "".join(cipherText)
  return cipherText