The code has a bug! It does not consider dashes while this is not specified in the description!
Of course, we could correct it by specifying this particularity in the DocString, or we could implement that in the code.
#### Corrected code
```
36    else:
37        tens_count = tens_letter_count[tens]
38        unit_count = count_letter_1_digits(unit)
39        count_letters = tens_count+unit_count
40        if unit_count != 0:
41            count_letters += len("-")
42        return count_letters
```
