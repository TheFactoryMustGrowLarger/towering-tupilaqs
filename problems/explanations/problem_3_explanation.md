The first 2 conditional statements will always be False, we are comparing a set and an integer they will always be different!
The code can be fixed by applying a len() function to the set of each function. Now we're comparing 2 integers as it was intended!
#### Corrected code
```
26 def all_numbers_are_the_same(numbers):
27     return len(set(numbers)) == 1
28
29
30 def two_numbers_are_the_same(numbers):
31     return len(set(numbers)) == 2
```
