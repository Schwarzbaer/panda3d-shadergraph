def linear(zero, one, gen=None):
    difference = one - zero
    def inner(x):
        if gen is not None:
            x = gen(x)
        value = zero + x * difference
        return value
    return inner


def exponential(exponent, gen=None):
    def inner(x):
        if gen is not None:
            x = gen(x)
        value = x ** exponent
        return value
    return inner
