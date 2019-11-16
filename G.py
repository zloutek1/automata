import sys
import types

from utils import Set


class G:
    def __init__(self, N, Σ, P, S):
        self.__dict__.update({
            "N": Set(map(str, N)),
            "Σ": Set(list(Σ)),
            "P": P,
            "S": str(S)})

    def __str__(self):
        return (f"G = ({self.N}, {self.Σ}, P, {self.S}) where\n" +
                "P = { " + "\n      ".join([f"{rule} -> {' | '.join(self.P[rule])}" for rule in self.P]) + " }")

    def __repr__(self):
        _name = self.__class__.__name__
        return f"{_name}({', '.join(str(key)+'='+', '.join(val) for key,val in self.__dict__.items())})"

    def toNFA(self):
        import NFA

        Q = Set(f"{A}̄" for A in self.N).union(Set("qf"))
        q0 = f"{self.S}̄"
        δ = NFA.δ(Q=Q, Σ=self.Σ)
        F = Set("S̄", "qf") if "ε" in self.P["S"] else Set("qf")

        M = NFA(Q, self.Σ, δ, q0, F)

        for A in self.N:
            for rule in self.P[A]:
                if len(rule) == 2:
                    a, B = rule
                    δ[f"{A}̄", a].add(f"{B}̄")

                elif len(rule) == 1 and rule != "ε":
                    a = rule
                    δ[f"{A}̄", a].add("qf")

        return M


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
        return G(*args, **kwargs)


sys.modules[__name__] = call()
