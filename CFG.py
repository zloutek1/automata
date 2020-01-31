import sys
import types

from utils import Set, all_subsets, Rule
from Analyzer import TopDownAnalyzer, BottomUpAnalyzer


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
                    # change rule A -> abcd... to A -> a<bcd...>
                    B, *C = rule

                    B1 = Rule(B if B.isupper() else f"{B}̄")
                    C1 = Rule((f"<{''.join(C)}>" if len(C) > 1 else
                               C[0] if C[0].isupper() else
                               f"{C[0]}̄"))

                    P[A].add(Rule(f"{B1}{C1}"))

                    A = Rule(f"{C1[0]}")

                    # continue generating <bcd...> -> b<cd...>
                    while len(A[0]) >= 2 and A[0] != "<>":
                        rule = Rule(f"{C1[0][1]}<{C1[0][2:-1]}>")
                        B, *C = rule

                        B1 = Rule(B if B.isupper() else f"{B}̄")
                        C1 = Rule((f"{''.join(C[0])}" if len(C[0]) > 1 else
                                   C[0] if C[0].isupper() else
                                   f"{C[0]}̄"))

                        P[A].add(Rule(f"{B1}{C1}"))

                        A = Rule(f"{C1[0]}")

                else:
                    P[A].add(Rule(rule))

            i += 1

        return CFG(N, self.Σ, P, self.S)

    def remove_left_recursion(self):
        def calc_potentials():
            potentials = {}
            for A in N:
                potentials.setdefault(A, Set())
                for rule in P[A]:
                    if rule[0] in N:
                        potentials[A].add(rule[0])
            return potentials

        N = self.N.copy()
        P = self.P.copy()

        for i, A in enumerate(N):
            for B in N[:i + 1]:
                if not B in calc_potentials()[A]:
                    continue

                if A == B:
                    α = [rule for rule in P[A] if rule.startswith(B)]
                    β = [rule for rule in P[A] if not rule.startswith(B)]
                    N = Set(f"{A}'").union(N)
                    P[f"{A}'"] |= Set(Rule(rule[1:]) for rule in α) | Set(
                        Rule(rule[1:] + f"{A}'") for rule in α)
                    P[A] = Set(Rule(rule) for rule in β) | Set(
                        Rule(rule + f"{A}'") for rule in β)

                else:
                    α = [rule for rule in P[A] if rule.startswith(B)]
                    β = [rule for rule in P[A] if not rule.startswith(B)]
                    P[A] = Set(Rule(rule) for rule in β) | Set(
                        Rule(ruleB + rule[1:]) for rule in α for ruleB in P[B])

        return CFG(N, self.Σ.copy(), P, self.S)

    def toGNF(self):
        """
        each rule must be of format
        A → aB1B2B3...Bn   (a ∈ Σ, B1,B2,B3,...,Bn ∈ N)
        """
        import CFG

        G = self.remove_left_recursion()
        N = Set(reversed(G.N.copy()))
        P = G.P.copy()

        def resolve(A, B):
            for _ in range(len(P[A])):
                rule = list(P[A].pop(0))
                if rule[0].islower():
                    for i, c in enumerate(rule[1:]):
                        if c.islower() and len(c) == 1:
                            rule[i + 1] = f"{c}̄"

                    rule = "".join(rule)
                    P[A].add(Rule(rule))

                elif rule[0] == B:
                    rules = Set()
                    for rule1 in P[B]:
                        rules.add(Rule(rule1 + "".join(rule[1:])))
                    P[A] |= rules

                else:
                    P[A].add(Rule(rule))

        for i, A in enumerate(N):
            for B in N[:i + 1]:
                resolve(A, B)

        return CFG(N, self.Σ, P, self.S)

    def toTopDownAnalyzer(self):
        import PDA
        L = self.remove_left_recursion()

        δ = PDA.δ()
        M = TopDownAnalyzer(Set("q"), L.Σ, L.N.union(L.Σ), δ, "q", L.S, Set())

        for A in L.N:
            for rule in L.P[A]:
                δ["q", "ε", A].add(("q", rule))

        for a in L.Σ:
            δ["q", a, a].add(("q", "ε"))

        return M

    def toBottomUpAnalyzer(self):
        import PDA
        # L = self.remove_left_recursion()
        L = self

        ô = PDA.ô()
        M = BottomUpAnalyzer(Set("q", "r"), L.Σ, L.N | L.Σ |
                             Set("⊥"), ô, "q", "⊥", Set("r"))

        for A in L.N:
            for rule in L.P[A]:
                ô["q", "ε", rule].add(("q", A))

        for a in L.Σ:
            ô["q", a, "ε"].add(("q", a))

        ô["q", "ε", "⊥S"].add(("r", "ε"))

        return M

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

    def copy(self):
        return P(super().copy())


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
