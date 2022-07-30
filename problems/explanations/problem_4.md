The code is bugged! The bug is in the last line, it is comparing a string to an int, of course, they will never be equal!
#### Corrected code
```
15    return (palindrome_base_10 == str(number))
```
