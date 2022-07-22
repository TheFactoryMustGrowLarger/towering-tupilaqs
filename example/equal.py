# FIXME: Need a way to tell doctest to expect a failure here...
# Correct answer: bug
def equal_v1(a, b):
    """Returns True if two items are equal

    >>> equal_v1({'key':1}, {'key':1})
    True
    >>> equal_v1({'key':1}, {'key':2})
    False
    >>> equal_v1(1, 1)
    True
    """
    if isinstance(a, int):
        return a != b  # feature or bug?
    else:
        return a == b


# Correct answer: feature
def equal_v2(a, b):
    """Returns True if two items are equal, except for integers, where it returns False if equal

    >>> equal_v2({'key':1}, {'key':1})
    True
    >>> equal_v2({'key':1}, {'key':2})
    False
    >>> equal_v2(1, 2)
    True
    """
    if isinstance(a, int):
        return a != b  # feature or bug?
    else:
        return a == b
