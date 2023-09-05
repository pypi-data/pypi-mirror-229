def _stringToNumbers(string):
  alphabet = "abcdefghijklmnopqrstuvwxyz"
  numberList = []
  for letter in string.lower():
    if letter == " ":
      number = 1000
    elif letter == "#": # punctuation placeholder character
      number = 1001
    else:
      number = alphabet.find(letter)
    numberList.append(number)
  return numberList

def _numbersToString(numbers):
  alphabet = "abcdefghijklmnopqrstuvwxyz"
  letterList = []
  for number in numbers:
    if number == 1000:
      letter = " "
    elif number == 1001: # punctuation placeholder character
      letter = "#"
    else:
      letter = alphabet[int(number)]
    letterList.append(letter)
  return "".join(letterList)