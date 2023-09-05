try: # attempt a relative import of the required modules
  from ._string_number_convert import _stringToNumbers as stringToNumbers
  from ._string_number_convert import _numbersToString as numbersToString
  from ._rebuild_key import _rebuildKey as rebuildKey
  from ._punctuation import _detectPunctuation as detectPunctuation
  from ._punctuation import _removePunctuation as removePunctuation
  from ._punctuation import _restorePunctuation as restorePunctuation
except: # if relative import fails, use a direct import instead
  from _string_number_convert import _stringToNumbers as stringToNumbers
  from _string_number_convert import _numbersToString as numbersToString
  from _rebuild_key import _rebuildKey as rebuildKey
  from _punctuation import _detectPunctuation as detectPunctuation
  from _punctuation import _removePunctuation as removePunctuation
  from _punctuation import _restorePunctuation as restorePunctuation

def vigenereCipher(plainText, key, encrypt = True):
  punctuation = detectPunctuation(plainText)
  plainText = removePunctuation(plainText, punctuation)

  plainTextLength = len(plainText)
  key = rebuildKey(plainText, key)

  numberList = stringToNumbers(plainText)
  numericKey = stringToNumbers(key)
  cipherNumbers = []
  
  for i in range(0, plainTextLength):
    plainNumber = numberList[i]
    shift = numericKey[i]

    if plainNumber == 1000:
      cipherNumbers.append(1000)
    else:
      if encrypt == True:
        shiftedNumber = (plainNumber + shift) % 26
      else:
        shiftedNumber = (plainNumber - shift) % 26
      cipherNumbers.append(shiftedNumber)

  cipherText = numbersToString(cipherNumbers)
  cipherText = restorePunctuation(cipherText, punctuation)
  return cipherText
