import sys
import types

from utils import Set
import FA


class DFA(FA.FA):
    """
    Deterministic finite automata

    each transition can have only one transition under each
    letter of the alphabet
    """

    def __init__(self, Q, Σ, δ, q0, F):
        """

        Q  : set of states
        Σ  : finite alphabet
        δ  : Q × Σ → Q transition function
        q0 : q0 ∈ Q initial state
        F  : F ⊆ Q set of accepting states

        """

        super().__init__(Q, Σ, δ, Set(q0), F)
        self.q0 = str(q0)
        self.δ.prepare(self.Q, self.Σ)

    def table(self):
        """

        create a table in this format:

            +---+---+---+
            |   | a | b |
            +---+---+---+
            | 1 | 2 | - |
            | 2 | 2 | 1 |
            +---+---+---+

        """

        super().table_header("DETERMINISTIC FINITE AUTOMATA")

        widths = [max([len(key[0]) - key[0].count("̂") for key in self.δ])]
        for a in self.Σ:
            widths.append(max(max([len(str(self.δ.get((qi, a), "")))
                                   for qi in self.Q]), len(a)))

        data = [("", *self.Σ)]
        for qi in self.Q:
            data.append([qi] + [str(self.δ.get((qi, a), "Ø")[0])
                                for a in self.Σ])

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

    def intersept(self, other):
        """
        create a new DFA which has:
            Q3 = Q1 × Q2
            F3 = F1 × F2
            q3 = (q1, q2)
            δ3((p, q), a) = (δ1(p, a), δ2(q, a))
        """

        Q3 = self.Q.cross(other.Q)
        F3 = self.F.cross(other.F)
        q3 = (self.q0, other.q0)

        δ3 = δ()

        for (p, q) in Q3:
            for a in self.Σ:
                if self.δ[p, a] != "-" and other.δ[q, a] != "-":
                    δ3[f"{(p, q)}", a] = f"{(self.δ[p, a], other.δ[q, a])}"

        M3 = DFA(Q3, self.Σ, δ3, q3, F3)
        return M3

    def __and__(self, other):
        return self.intersept(other)

    def union(self, other):
        """
        return a new DFA which has:
            Q3 = Q1 × Q2
            F3 = F1 × Q2 ∪ Q1 × F2
            q3 = (q1, q2)
            δ3((p, q), a) = (δ1(p, a), δ2(q, a))
        """

        M3 = self.intersept(other)
        M3.F = self.F.cross(other.Q).union(self.Q.cross(other.F))
        return M3

    def __or__(self, other):
        return self.union(other)

    def minimize(self):
        """
        in order to minimize folow these steps:
            1. add hell if necessary
            2. remove unreachable nodes
            3. start reduction
            4. order properly
        """

        self._add_hell()
        self._remove_unreachables()
        reduced = self._reduce()
        canonized = reduced._canonize()
        return canonized

    def _remove_unreachables(self):
        unreachables = self.δ.unreachables(self.q0)

        self.Q -= unreachables
        self.F -= unreachables

        for unreachable in unreachables:
            for a in self.Σ:
                del self.δ[unreachable, a]

        self.δ.Q = self.Q

    def _add_hell(self):
        addedHell = False
        for qi in self.Q:
            for a in self.Σ:
                if self.δ.get((qi, a)) is not None and self.δ[qi, a] != "-":
                    continue

                if not addedHell:
                    addedHell = True
                    self.Q.add("⊗")
                    for a2 in self.Σ:
                        self.δ["⊗", a2] = "⊗"

                self.δ[qi, a] = "⊗"

    def _reduce(self, imax=None):
        from utils import roman
        import DFA

        def init(i):
            """
            split into two groups
            I  - non terminal
            II - terminal
            """
            groups = {
                qi: roman(1) if qi not in self.F else roman(2)
                for qi in self.Q
            }

            δ = DFA.δ(Q=self.Q, Σ=self.Σ)
            for qi in (self.Q - self.F) + self.F:
                for a in self.Σ:
                    δ[qi, a] = groups.get(self.δ[qi, a])

            if imax is None or i < imax:
                return step(i + 1, groups, δ)
            return groups, δ

        def step(i, groups, δ):
            new_groups = {}
            force_move = 0
            numeratd_patterns = []
            for i in range(len(Set(groups.values()))):
                for qi, val in groups.items():
                    target = δ.group()[qi]
                    if val == roman(i + 1):
                        if target not in numeratd_patterns:
                            numeratd_patterns.append(target)
                        index = numeratd_patterns.index(target)
                        new_groups[qi] = roman(index + 1 + force_move)
                force_move += len(numeratd_patterns)
                numeratd_patterns = []

            new_δ = DFA.δ()
            for qi in self.Q:
                for a in self.Σ:
                    new_δ[qi, a] = new_groups.get(self.δ[qi, a])

            if (imax is None or i < imax) and groups != new_groups and δ != new_δ:
                return step(i + 1, new_groups, new_δ)
            return new_groups, new_δ

        groups, new_δ = init(0)

        Q = Set(groups.values())
        q0 = groups[self.q0]

        δ = DFA.δ()
        for (qi, a), target in new_δ.items():
            δ[groups[qi], a] = target

        F = Set(groups[qf] for qf in self.F)
        return DFA(Q, self.Σ, δ, q0, F)

    def _canonize(self):
        import DFA

        Q = Set(chr(ord('A') + i) for i in range(len(self.Q)))
        letterMapping = dict(zip(self.δ.reachables(self.q0), Q))

        δ = DFA.δ()
        for (qi, a), target in self.δ.items():
            δ[letterMapping[qi], a] = letterMapping[target]

        q0 = letterMapping[self.q0]
        F = Set(letterMapping[qf] for qf in self.F)

        return DFA(Q, self.Σ, δ, q0, F)

    def test(self, word):
        word = list(word)
        qi = self.q0
        while len(word) > 0:
            a = word.pop(0)
            qi = self.δ[qi, a]
        return qi in self.F


class δ(FA.δ):
    """
    inherited from FA.δ, look there for more information
    """

    def __setitem__(self, key, val):
        if val == "-":
            return  # no path

        q, a = map(str, key)
        super().__setitem__((q, a), Set(str(val)))

    def __getitem__(self, key):
        key = tuple(map(str, key))
        if key not in self:
            return "-"
        return super().__getitem__(key)[0]

    def items(self):
        return list((k, v[0]) for k, v in super().items())

    def reachables(self, q0):
        """
        return a list of all reachable qi states from the state q0
        """

        result = Set()
        stack = [q0]

        while len(stack) > 0:
            q = stack.pop(0)
            result.add(q)
            for a in self.Σ:
                target = self.__getitem__((q, a))
                if target is not None:
                    if target not in result:
                        stack.append(target)
                    result.add(target)

        return result

    def unreachables(self, q0):
        return self.fa.Q - self.reachables(q0)


class call(types.ModuleType):
    """
    make the module callable simplifying
    from DFA import DFA
    to
    import DFA
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return DFA(*args, **kwargs)


sys.modules[__name__] = call()
