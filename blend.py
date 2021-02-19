class BlendingFunction:
    def __init__(self, *parameters):
        if isinstance(parameters[-1], BlendingFunction):
            self.gen = parameters[-1]
            parameters = parameters[:-1]
        else:
            self.gen = None
        self.init(*parameters)

    def __call__(self, x):
        if self.gen is not None:
            x = self.gen(x)
        return self.calc(x)


class Linear(BlendingFunction):
    def init(self, zero, one):
        self.zero = zero
        self.difference = one - zero

    def calc(self, x):
        return self.zero + x * self.difference


class Exponential(BlendingFunction):
    def init(self, exponent):
        self.e = exponent

    def calc(self, x):
        return x ** self.e
