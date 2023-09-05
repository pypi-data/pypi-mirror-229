def polybusSquare(plainText, encrypt = True):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    numbers = "12345"
    square = [
        ["a", "b", "c", "d", "e"],
        ["f", "g", "h", "i", "k"],
        ["l", "m", "n", "o", "p"],
        ["q", "r", "s", "t", "u"],
        ["v", "w", "x", "y", "z"]
    ]
    cipherText = []
    plainText = list(plainText)

    # detect all foreign characters
    foreignCharacters = []
    for character in plainText:
        if encrypt == True: # if encrypting, remove all non alphabetic characters
            if character not in alphabet:
                foreignCharacters.append(character)
        else:
            if character not in numbers: # if decrypting, remove all non numeric characters
                foreignCharacters.append(character)
    # remove all foreign characters
    for character in foreignCharacters:
        plainText.remove(character)

    if encrypt == True:
        for letter in plainText:
            index = findInSquare(square, letter)
            cipherText.append(index)
    else:
        for i in range(0, len(plainText), 2):
            row = int(plainText[i]) - 1
            column = int(plainText[i + 1]) - 1
            letter = square[row][column]
            cipherText.append(letter)

    cipherText = "".join(cipherText)
    return cipherText
        
def findInSquare(square, targetLetter):
    for rowIndex, row in enumerate(square):
        for columnIndex, letter in enumerate(row):
            if letter == targetLetter:
                index = str(rowIndex + 1) + str(columnIndex + 1) # add 1 to each index to make them start at 1 instead of 0
                return index