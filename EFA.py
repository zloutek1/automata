import sys
import types

from utils import Set
import FA
from NFA import NFA


class EFA(NFA):
    def __init__(self, Q, Σ, δ, q0, F):
        Σ += Set("ε")
        super().__init__(Q, Σ, δ, q0, F)

    def table(self):
        super().table_header("NON-DETERMINISTIC FINITE AUTOMATA with ε steps")

        widths = [max([len(key[0]) - key[0].count("̂") for key in self.δ])]
        for a in self.Σ:
            widths.append(max(max([len(str(self.δ.get((qi, a), "")))
                                   for qi in self.Q]), len(a)))
        widths.append(max([len(str(self.δ.Dε(qi))) for qi in self.Q]))

        data = [("", *self.Σ, "Dε")]
        for qi in self.Q:
            data.append([qi] +
                        [str(self.δ.get((qi, a), "Ø")) for a in self.Σ] +
                        [str(self.δ.Dε(qi))])

        def sep():
            print("+" + "+".join([f"-{'-' * w}-" for w in widths]) + "+")

        def print_row(i):
            print("|" +
                  "|".join([
                      f" {data[i][col].center(w + data[i][0].count('̄'))} "
                      for col, w in enumerate(widths)]) +
                  "|")

        def print_content():
            sep()
            print_row(0)
            sep()
            for i in range(1, len(self.δ.group()) + 1):
                print_row(i)
            sep()

        super().table_body(print_content)

    def toNFA(self):
        import NFA

        δ = NFA.δ(Q=self.Q, Σ=self.Σ)
        for qi in self.Q:
            for a in self.Σ:
                if a == "ε":
                    continue

                step1 = self.δ.get((qi, a), Set())

                step2 = Set()
                for s in self.δ.Dε(qi):
                    step2 |= self.δ.get((s, a), Set())

                step3 = Set()
                for s in step1 | step2:
                    step3 |= self.δ.Dε(s)

                δ[qi, a] = tuple(step3)

        Σ = self.Σ - Set("ε")
        F = (self.F if self.δ.Dε(self.q0).intercept(self.F) == Set() else
             self.F.union(Set(self.q0)))

        return NFA(self.Q, Σ, δ, self.q0, F)

    def toDFA(self):
        return self.toNFA().toDFA()


class δ(FA.δ):
    def __setitem__(self, key, val):
        if len(key) == 2:
            super().__setitem__(tuple(map(str, key)), Set(map(str, val)))

        elif len(key) > 2 and len(key) == len(val) + 1:
            for k, v in zip(key[1:], val):
                self.__setitem__((key[0], k), v)

    def __getitem__(self, key):
        key = tuple(map(str, key))
        return super().__getitem__(key)

    def Dε(self, q0):
        result = Set()
        stack = [q0]
        while len(stack) > 0:
            q = stack.pop(0)
            result.add(q)
            targets = self.__getitem__((q, "ε"))
            for target in targets:
                if target not in result:
                    stack.append(target)
                result.add(target)
        return result


class ô(δ, FA.ô):
    def __getitem__(self, key):
        qi, word = key

        if word == "ε":
            return EFA.Dε(qi)
        return super().__getitem__(key)


class call(types.ModuleType):
    """
    make the module callable simplifying
    from EFA import EFA
    to
    import EFA
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return EFA(*args, **kwargs)


sys.modules[__name__] = call()
