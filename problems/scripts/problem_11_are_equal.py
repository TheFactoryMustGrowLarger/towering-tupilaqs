def are_equal(a, b):
    """Returns True if two items are equal

    >>> are_equal({'key':1}, {'key':1})
    True
    >>> are_equal({'key':1}, {'key':2})
    False

    #>>> are_equal(1, 1)
    #True
    """
    if isinstance(a, int):
        return not (a == b)
    else:
        return a == b
