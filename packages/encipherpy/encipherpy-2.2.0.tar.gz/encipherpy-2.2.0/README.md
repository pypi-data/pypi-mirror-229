# Encipherpy

Encipherpy is a python package that contains the implementations of multiple ciphers.

## Supported ciphers

| Cipher              | Import code                                                     | Arguments                                          |
| ------------------- | --------------------------------------------------------------- | -------------------------------------------------- |
| Caesar              | `from encipherpy.caesar_cipher import caesarCipher`             | str`plainText`, int`key`, bool`encrypt`            |
| Vigènere            | `from encipherpy.vigenere_cipher import vigenereCipher`         | str`plainText`, str`key`, bool`encrypt`            |
| Rot47               | `from encipherpy.rot47_cipher import rot47`                     | str`plainText`                                     |
| Atbash              | `from encipherpy.atbash_cipher import atbashCipher`             | str`plainText`                                     |
| Simple substitution | `from encipherpy.substitution_cipher import substitutionCipher` | str`plainText`, str`cipherAlphabet`, bool`encrypt` |
| Polybus square      | `from encipherpy.polybus_square_cipher import polybusSquare`    | str`plainText`, bool`encrypt`                      |
