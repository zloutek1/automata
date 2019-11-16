import sys
import types

from utils import Set


class CFG:
    def __init__(self, N, Σ, P, S):
        self.__dict__.update({
            "N": Set(map(str, N)),
            "Σ": Set(list(Σ)),
            "P": P,
            "S": str(S)})

    def Ne(self):
        import re
        i = 0
        N = {0: Set()}

        def do():
            nonlocal i, N
            i = i + 1
            N[i] = N[i - 1].union(Set(A for A in self.N for p in self.P[A]
                                      if re.sub("[∅" + "".join(N[i - 1]) + "]", "", p).islower()))

        do()
        while N[i] != N[i - 1]:
            do()

        Ne = N[i]
        return Ne

    def __str__(self):
        return (f"G = ({self.N}, {self.Σ}, P, {self.S}) where\n" +
                "P = { " + "\n      ".join([f"{rule} -> {' | '.join(self.P[rule])}" for rule in self.P]) + " }")

    def __repr__(self):
        _name = self.__class__.__name__
        return f"{_name}({', '.join(str(key)+'='+', '.join(val) for key,val in self.__dict__.items())})"


class P(dict):
    def __init__(self, *args, **kwargs):
        if (len(args) == 1 and isinstance(args[0], dict)):
            for k, v in args[0].items():
                self.__setitem__(k, v)
            super().__init__(**kwargs)
        else:
            super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, list(map(str.strip, value.split("|"))))


class call(types.ModuleType):
    """
    make the module callable simplifying
    from G import G
    to
    import G
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return CFG(*args, **kwargs)


sys.modules[__name__] = call()
