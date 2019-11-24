import sys
import types

from utils import Set
import FA


class NFA(FA.FA):
    """
    Non-Deterministic finite automata

    each transition can have multiple transitions under same
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

    def table(self):
        """

        create a table in this form:

            +---+-----+--------+--------+--------+
            |   |  a  |   b    |   c    |   d    |
            +---+-----+--------+--------+--------+
            | 1 |  Ø  |  {1}   |   Ø    |  {1}   |
            | 2 |  Ø  |  {1,2} |  {2}   |   Ø    |
            +---+-----+--------+--------+--------+


        """

        super().table_header("NON-DETERMINISTIC FINITE AUTOMATA")

        widths = [max([len(key[0]) - key[0].count("̂") for key in self.δ])]
        for a in self.Σ:
            col = []
            for qi in self.Q:
                val = str(self.δ.get((qi, a)))
                col.append(len(val) - val.count("̂"))
            widths.append(max(col))

        data = [("", *self.Σ)]
        for qi in self.Q:
            data.append([qi] + [str(self.δ.get((qi, a), "Ø")) for a in self.Σ])

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

    def toDFA(self):
        """
        convert NFA to DFA
        """
        import DFA

        def rename_state(state):
            import re
            return re.sub(r"[\{\}\,\sØ]", r"", f"[{state}]")

        q0 = rename_state(Set(self.q0))
        Q = Set(Set(self.q0))
        δ = DFA.δ(Σ=self.Σ)
        F = Set()
        Done = Set()

        while (Q - Done) != Set():
            M = (Q - Done).pop(0)
            if M.intercept(self.F) != Set():
                F = F.union(Set(M))
            for a in self.Σ:
                N = Set.Union([self.δ[p, a] for p in M])
                Q = Q.union(Set(N))
                δ[M, a] = N
            Done = Done.union(Set(M))

        Q = Set([rename_state(qi) for qi in Q])
        δ = DFA.δ({(rename_state(qi), a): rename_state(target)
                   for (qi, a), target in δ.items()}, Q=Q, Σ=self.Σ)
        F = Set([rename_state(qf) for qf in F])

        return DFA(Q, self.Σ, δ, q0, F)


class δ(FA.δ):
    """
    inherited from FA.δ, look there for more information
    """

    def __setitem__(self, key, val):
        if len(key) == 2:
            super().__setitem__(tuple(map(str, key)), Set(map(str, val)))

        elif len(key) > 2 and len(key) == len(val) + 1:
            for k, v in zip(key[1:], val):
                self.__setitem__((key[0], k), v)

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, Set())
        return super().__getitem__(key)


class ô(FA.ô):
    """
    inherited from FA.δ, look there for more information
    """

    def __getitem__(self, key):
        qi, word = key

        if word == "ε":
            return Set(qi)
        return super().__getitem__(key)


class call(types.ModuleType):
    """
    make the module callable simplifying
    from NFA import NFA
    to
    import NFA
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return NFA(*args, **kwargs)


sys.modules[__name__] = call()
