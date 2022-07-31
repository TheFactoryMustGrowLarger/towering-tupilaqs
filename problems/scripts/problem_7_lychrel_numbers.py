def is_lychrel(number):
    """This function assesses whether an integer is a Lychrel number or not.

    A Lychrel number is a natural number that cannot form a palindrome through the iterative process of
    repeatedly reversing its digits and adding the resulting numbers.
    Example of Non-Lychrel numbers:
    56, 56+65 = 121 it becomes palindromic in one iteration.
    59, 59+95 = 154, 154+451 = 605, 605+506 = 1111 it becomes palindromic in three iteration.
    Example of Lychrel numbers:
    196, 196+691 = 887, 887+788 = 1675 it is not proven yet, but it's thought that it will never produce a palindrome.
    It is assumed that if a number does not produce a palindrome after 50 iterations,
    it can be considered a Lychrel number.
    """
    sum_numbers = number
    for _ in range(50):
        sum_numbers += __get_inverse(sum_numbers)
        if __is_palindromic(sum_numbers):
            return False
    return True


def __is_palindromic(number):
    return __get_inverse(number) == number


def __get_inverse(number):
    return int(str(number)[::-1])
