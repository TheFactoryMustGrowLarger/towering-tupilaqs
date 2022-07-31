def equal_except_integers(a, b):
    """Returns True if two items are equal, except for integers, where it returns False if equal

    >>> equal_except_integers({'key':1}, {'key':1})
    True
    >>> equal_except_integers({'key':1}, {'key':2})
    False
    >>> equal_except_integers(1, 2)
    True
    """
    if isinstance(a, int):
        return not (a == b)
    else:
        return a == b
