from math import sqrt


def is_truncatable(number):
    """This function returns whether a number is truncatable or not.

    A truncatable prime is a prime number that when you successively remove digits from one end of the prime,
    you are left with a new prime number. Single digit numbers are never considered truncatable.
    """
    if len(str(number)) == 1:
        return False
    return (__is_truncatable_from_left(number)) and (__is_truncatable_from_right(number))


def __is_truncatable_from_left(number):
    while number != "":
        if __is_prime(int(number)) is False:
            return False
        number = str(number)[1:]
    return True


def __is_truncatable_from_right(number):
    while number != "":
        if __is_prime(int(number)) is False:
            return False
        number = str(number)[:-1]
    return True


def __is_prime(number):
    for x in range(2, int(sqrt(number))+1):
        if number % x == 0:
            return False
    return True
