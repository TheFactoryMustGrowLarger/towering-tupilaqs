def is_double_base_palindrome(number):
    """The function assesses whether a number is a palindrome in base ten and base two."""
    number_in_base_2 = __to_base_2(number)
    return __is_palindrome(number) and __is_palindrome(number_in_base_2)


def __to_base_2(number):
    return bin(number)[2:]


def __is_palindrome(number):
    palindrome_base_10 = str(number)[::-1]
    return (palindrome_base_10 == number)
