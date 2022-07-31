import random


def slot_machine():
    """The following simulates a slot machine with three entries.

    Each entry shows a number between 0 and 9.
    It will always return the numbers rolled and a message.
    If all the numbers are the same, the message is "Jackpot!",
    if two numbers are the same, the message is "Good roll" and
    if they are all different, the message is "Try again, you will be luckier".
    """
    digits = range(10)
    first_n = random.choice(digits)
    second_n = random.choice(digits)
    third_n = random.choice(digits)
    roll = [first_n, second_n, third_n]
    if __all_numbers_are_the_same(roll):
        return roll, "Jackpot!"
    elif __two_numbers_are_the_same(roll):
        return roll, "Good roll!"
    else:
        return roll, "Try again, you will be luckier!"


def __all_numbers_are_the_same(numbers):
    return set(numbers) == 1


def __two_numbers_are_the_same(numbers):
    return set(numbers) == 2
