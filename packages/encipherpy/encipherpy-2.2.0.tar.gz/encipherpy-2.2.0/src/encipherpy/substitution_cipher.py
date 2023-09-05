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

def substitutionCipher(plainText, cipherAlphabet, encrypt = True):
    punctuation = detectPunctuation(plainText)
    plainText = removePunctuation(plainText, punctuation)

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    cipherLetters = []

    indexes = []
    # get the alphabet index of each letter in the plainText
    for letter in plainText:
        if encrypt == True: # if encrypting, get the standard alphabet index
            index = alphabet.find(letter)
        else: # if decrypting, get the cipher alphabet index
            index = cipherAlphabet.find(letter)
        indexes.append(index)

    for i in range(len(plainText)):
        if plainText[i] == " ":
            cipherLetter = " "
        else:
            index = indexes[i]
            if encrypt == True: # if encrypting, get the cipherLetter from the cipher alphabet
                cipherLetter = cipherAlphabet[index]
            else: # if decrypting, get the cipherLetter from the standard alphabet
                cipherLetter = alphabet[index]
        cipherLetters.append(cipherLetter)

    cipherText = "".join(cipherLetters)
    cipherText = restorePunctuation(cipherText, punctuation)
    return cipherText