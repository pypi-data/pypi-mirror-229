try: # attempt a relative import of the required modules
  from ._string_number_convert import _stringToNumbers as stringToNumbers
  from ._string_number_convert import _numbersToString as numbersToString
  from ._punctuation import _detectPunctuation as detectPunctuation
  from ._punctuation import _removePunctuation as removePunctuation
  from ._punctuation import _restorePunctuation as restorePunctuation
except: # if relative import fails, use a direct import instead
  from _string_number_convert import _stringToNumbers as stringToNumbers
  from _string_number_convert import _numbersToString as numbersToString
  from _punctuation import _detectPunctuation as detectPunctuation
  from _punctuation import _removePunctuation as removePunctuation
  from _punctuation import _restorePunctuation as restorePunctuation

def caesarCipher(plainText, key, encrypt = True):
  punctuation = detectPunctuation(plainText)
  plainText = removePunctuation(plainText, punctuation)

  numberText = stringToNumbers(plainText)
  cipherNumbers = []

  for number in numberText:
    if number >= 1000: # if the number is reserved by the converters, append to the list without shifting
      cipherNumbers.append(number)
    else:
      if encrypt:
        shiftedNumber = (number + key) % 26
      else:
        shiftedNumber = (number - key) % 26
      cipherNumbers.append(shiftedNumber)

  cipherText = numbersToString(cipherNumbers)
  cipherText = restorePunctuation(cipherText, punctuation)
  return cipherText
