def count_ways_to_make_number(number_to_make, *available_numbers):
    """The following counts the number of possible ways to make a certain number using only available numbers.

    Example:
    number_to_make = 5 available_numbers = [1,2,3]
    Possible ways:
    1 1 1 1 1
    2 1 1 1
    2 2 1
    3 1 1
    3 2
    Hence the number of ways is equal to 5.
    """
    values = {x: 0 for x in range(number_to_make+1)}
    values[0] = 1
    for coin in available_numbers:
        for number in values:
            if number >= coin:
                values[number] += values[number-coin]
    number_of_ways = values[number_to_make]
    return number_of_ways
