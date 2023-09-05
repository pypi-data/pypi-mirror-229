try: # attempt a relative import of the required modules
  from ._punctuation import _detectPunctuation as detectPunctuation
  from ._punctuation import _removePunctuation as removePunctuation
  from ._punctuation import _restorePunctuation as restorePunctuation
except: # if relative import fails, use a direct import instead
  from _punctuation import _detectPunctuation as detectPunctuation
  from _punctuation import _removePunctuation as removePunctuation
  from _punctuation import _restorePunctuation as restorePunctuation

def atbashCipher(plainText):
  plainText = plainText.lower()
  punctuation = detectPunctuation(plainText)
  plainText = removePunctuation(plainText, punctuation)

  cipherLetters = []
  
  for letter in plainText:
    match letter:
      case "a":
        cipherLetters.append("z")
      case "b":
        cipherLetters.append("y")
      case "c":
        cipherLetters.append("x")
      case "d":
        cipherLetters.append("w")
      case "e":
        cipherLetters.append("v")
      case "f":
        cipherLetters.append("u")
      case "g":
        cipherLetters.append("t")
      case "h":
        cipherLetters.append("s")
      case "i":
        cipherLetters.append("r")
      case "j":
        cipherLetters.append("q")
      case "k":
        cipherLetters.append("p")
      case "l":
        cipherLetters.append("o")
      case "m":
        cipherLetters.append("n")
      case "n":
        cipherLetters.append("m")
      case "o":
        cipherLetters.append("l")
      case "p":
        cipherLetters.append("k")
      case "q":
        cipherLetters.append("j")
      case "r":
        cipherLetters.append("i")
      case "s":
        cipherLetters.append("h")
      case "t":
        cipherLetters.append("g")
      case "u":
        cipherLetters.append("f")
      case "v":
        cipherLetters.append("e")
      case "w":
        cipherLetters.append("d")
      case "x":
        cipherLetters.append("c")
      case "y":
        cipherLetters.append("b")
      case "z":
        cipherLetters.append("a")
      case " ":
        cipherLetters.append(" ")
      case "#":
        cipherLetters.append("#")

  cipherText = "".join(cipherLetters)
  cipherText = restorePunctuation(cipherLetters, punctuation)
  return cipherText