def are_amicable(a, b):
    """This function returns True if a and b are amicable and False if they're not amicable.

    Two numbers are amicable if each is equal to the sum of the proper divisors of the other.
    Example:
    220 and 284:
    Sum of divisors of 220 = 284
    Sum of divisors of 284 = 220
    """
    return __sum_of_divisors(a) == b and __sum_of_divisors(b) == a


def __sum_of_divisors(number):
    return sum(__proper_divisors(number))


def __proper_divisors(number):
    divisors = list()
    for i in range(1, number+1):
        if number % i == 0:
            divisors.append(i)
    return divisors
