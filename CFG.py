import sys
import types

from utils import Set, all_subsets, Rule


class CFG:
    """
    Context Free Grammar

    each rule must be A →

    """

    def __init__(self, N, Σ, P, S):
        if not isinstance(N, Set):
            raise ValueError("N must be set of strings")
        if not isinstance(Σ, Set):
            raise ValueError("N must be set of strings")

        self.__dict__.update({
            "N": N,
            "Σ": Σ,
            "P": P,
            "S": str(S)})

    @property
    def Ne(self):
        """
        get all normalised nonterminals
        """

        import re
        i = 0
        N = {0: Set()}

        def do():
            nonlocal i, N
            i = i + 1
            N[i] = N[i - 1].union(Set(A for A in self.N for p in self.P[A]
                                      if re.sub("[∅" + "".join(N[i - 1]) + "]", "", str(p)).islower()))

        do()
        while N[i] != N[i - 1]:
            do()

        Ne = N[i]
        return Ne

    @property
    def V(self):
        """
        get all reachable symbols
        """
        i = 0
        V = {0: Set(self.S)}

        def do():
            nonlocal i, V
            i = i + 1
            V[i] = V[i - 1].union(Set(sym for sym in self.N.union(self.Σ)
                                      if any(sym in rule for A in V[i - 1] if A.isupper() for rule in self.P[A])))

        do()
        while V[i] != V[i - 1]:
            do()

        V = V[i]
        return V

    def reduce(self):
        import CFG

        N = self.N.copy()
        Σ = self.Σ.copy()
        P = self.P.copy()

        G = CFG(N, Σ, P, self.S)

        # remove non-reduced terminals
        nonreduced = N - G.Ne
        for A in nonreduced:
            # remove whole rule
            del P[A]
            N.remove(A)

            # remove each option with that rule
            for B, options in P.items():
                for opt in options:
                    if A in opt:
                        P[B].remove(opt)

        return G.remove_unreachable()

    def remove_unreachable(self):
        N, Σ, P = self.N.copy(), self.Σ.copy(), self.P.copy()

        unreachable = N.union(self.Σ) - self.V
        for X in unreachable:
            # remove non-terminals
            if X.isupper():
                del P[X]
                N.remove(X)

            # remove terminals
            else:
                Σ.remove(X)

        return CFG(N, Σ, P, self.S)

    @property
    def Nε(self):
        """
        get all states that can turn into ε
        """

        import re
        i = 0
        N = {0: Set()}

        def do():
            nonlocal i, N
            i = i + 1
            N[i] = N[i - 1].union(Set(A for A in self.N for p in self.P[A]
                                      if re.sub("[∅ε" + "".join(N[i - 1]) + "]", "", str(p)) == ""))
        do()
        while N[i] != N[i - 1]:
            do()

        Nε = N[i]
        return Nε

    def remove_ε(self):
        import CFG
        import re

        Nε = self.Nε

        N = self.N
        S = self.S
        P = CFG.P()

        for A in self.N:
            P[A] = self.P[A] - Set("ε")
            for opt in P[A]:
                for subset in all_subsets(Nε):
                    new_opt = re.sub(f"[ε{''.join(subset)}]", "", str(opt))
                    if new_opt != "":
                        P[A].add(new_opt)

        for opt in self.P[self.S]:
            if all(X in Nε for X in opt):
                N |= (Set("S'"))
                S = "S'"
                P["S'"] = f"ε | {self.S}"
                break

        G = CFG(N, self.Σ, P, S)
        return G

    def Nx(self, x):
        i = 0
        N = {0: Set(x)}

        def do():
            nonlocal i, N
            i = i + 1
            N[i] = N[i - 1].union(Set(rule for A in N[i - 1]
                                      for rule in self.P[A] if self.isprimitive(rule)))

        do()
        while N[i] != N[i - 1]:
            do()

        Nx = N[i]
        return Nx

    def remove_primitive_rules(self):
        """
        remove all rules of type A → B where A,B ∈ N
        """
        import CFG

        P = CFG.P()

        for A in self.N:
            NA = self.Nx(A)
            P[A] = Set(rule for B in NA for rule in self.P[B]
                       if not self.isprimitive(rule))

        return CFG(self.N, self.Σ, P, self.S)

    @staticmethod
    def isprimitive(rule):
        return len(rule) == 1 and rule.isupper()

    def toOwn(self):
        A = self.remove_ε()
        B = A.remove_primitive_rules()
        C = B.reduce()
        return C

    def toCNF(self):
        """
        each rule must be of format
        A → BC   (A,B,C ∈ N)
        A → a    (A ∈ N, a ∈ Σ)
        S → ε    if S is not on the right side of any rule
        """
        import CFG

        G = self.toOwn()
        N = G.N.copy()
        P = CFG.P()

        i = 0
        while i < len(N):
            A = N[i]
            for rule in G.P.get(A, P[A]):
                A = N[i]
                if len(rule) >= 2:
                    B, *C = rule

                    B1 = Rule(B if B.isupper() else f"{B}̄")
                    C1 = Rule((f"<{''.join(C)}>" if len(C) > 1 else
                               C[0] if C[0].isupper() else
                               f"{C[0]}̄"))

                    P[A].add(Rule(f"{B1}{C1}"))

                    A = Rule(f"<{C1[0]}>")
                    rule = Rule(f"{C1[0][0]}<{C1[0][1:]}>")

                    while len(A[0]) >= 2:
                        B, *C = rule

                        B1 = Rule(B if B.isupper() else f"{B}̄")
                        C1 = Rule((f"<{''.join(C[0])}>" if len(C[0]) > 1 else
                                   C[0] if C[0].isupper() else
                                   f"{C[0]}̄"))

                        P[A].add(Rule(f"{B1}{C1}"))

                        A = Rule(f"<{C1[0]}>")
                        rule = Rule(f"{C1[0][0]}<{C1[0][1:]}>")

                else:
                    P[A].add(Rule(rule))

            i += 1

        return CFG(N, self.Σ, P, self.S)

    def __getattr__(self, key):
        if key.startswith("N") and key[1:] in self.N:
            return self.Nx(key[1:])
        super().__getattr__(key)

    def __str__(self):
        return (f"G = ({self.N}, {self.Σ}, P, {self.S}) where\n" +
                "P = { " + "\n      ".join([f"{rule} -> {' | '.join(map(str, self.P[rule]))}" for rule in self.P]) + " }")

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
        if isinstance(value, str):
            super().__setitem__(key, Set(map(Rule, map(str.strip, value.split("|")))))

        elif isinstance(value, Set):
            super().__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self:
            super().__setitem__(key, Set())
        return super().__getitem__(key)


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
