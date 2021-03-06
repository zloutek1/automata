from collections.abc import Iterable
from utils import Set


class FA:
    def __init__(self, Q, Σ, δ, I, F):
        """

        Q : set of states
        Σ : finite alphabet
        δ : Q × Σ → Q transition function
        I : I ⊆ Q set of initial states
        F : F ⊆ Q set of accepting states

        """
        import FA

        assert isinstance(Q, Set), "Q must be a Set of states"
        assert isinstance(Σ, Set), "Σ must be a Set of alphabet"
        assert isinstance(
            δ, FA.δ), f"δ must be a transition function FA.δ, but is {type(δ)}"
        assert isinstance(I, Set), "I must be a Set of initial states"
        assert all(q0 in Q for q0 in I) or I.empty(
        ), f"condition I ⊆ Q not met, element of {I} not in {Q}"
        assert isinstance(F, Set), "F must be a Set of accepting states"
        assert all(qf in Q for qf in F) or F.empty(
        ), f"condition F ⊆ Q not met, element of {F} not in {Q}"

        self.__dict__.update({
            "Q": Q.map(str), "Σ": Σ.map(str), "δ": δ, "I": I.map(str), "F": F.map(str)})

        self.δ.fa = self

    def table_header(self, text):
        """

        print
        +-----------------+
        | place text here |
        +-----------------+

        """
        print("+-" + "-" * max(len(text), 40) + "-+")
        print("| " + text.center(max(len(text), 40)) + " |")
        print("+-" + "-" * max(len(text), 40) + "-+")

    def table_body(self, print_content):
        print()
        print("Q  =", self.Q)
        print("Σ  =", self.Σ)
        print()

        print_content()

        print()
        print("I =", self.I)
        print("F  =", self.F)

    def diagram(self, filename=None, *, δ=None):
        """

        export an image containing the digraph representation
        of the automata

        """

        import graphviz as gv
        δ = δ if δ else self.δ

        G = gv.Digraph('finite_state_machine', format="png")
        G.attr(rankdir='LR', size='8,5')

        # add end nodes
        G.attr('node', shape='doublecircle')
        for qf in self.F:
            G.node(str(qf))

        # add starting arrow
        for q0 in self.I:
            G.attr('node', shape='point')
            G.node("")
            G.attr('node', shape='circle')
            G.edge("", q0, label="")

        # add DFA transitions
        if self.__class__.__name__ == "DFA":
            G.attr('node', shape='circle')
            for key in δ:
                target = δ.get(key)[0]
                initial = key[0]
                value = key[1]
                if target != "-":
                    G.edge(initial, target, label=value)

            filename = self.__class__.__name__ if filename is None else filename
            G.render("images/" + filename, view=False)

        # add NFA transitions
        else:
            G.attr('node', shape='circle')
            for key in δ:
                targets = δ.get(key)
                initial = key[0]
                value = key[1]
                for target in targets:
                    G.edge(initial, str(target), label=value)

            filename = self.__class__.__name__ if filename is None else filename
            G.render("images/" + filename, view=False)

    def __str__(self):
        return (f"A = ({self.Q}, {self.Σ}, δ, {self.I}, {self.F}) where\n" +
                f"δ = {self.δ}")

    def __repr__(self):
        _name = self.__class__.__name__
        return f"{_name}({', '.join(str(key)+'='+str(val) for key,val in self.__dict__.items())})"


class δ(dict):
    """

    add transition in formats
    δ[q1, a] = q2
    δ[q1, a] = {q2, q3}

    δ[q1, a, b, c] = (q2, q3, q4)
    δ[q1, a, b, c] = ({}, {q2, q3}, {q4})

    """

    def __init__(self, *args, automata=None, **kwargs):
        self.fa = automata

        super().__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        q, a = map(str, key)
        super().__setitem__((q, a), val.map(str))

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, Set())
        return super().__getitem__(key)

    def prepare(self, Q, Σ):
        """

        set each transition (q, a) to "-"

        """

        self.Q = Q
        self.Σ = Σ
        for qi in Q:
            for a in Σ:
                if super().get((qi, a)) is None:
                    super().__setitem__((qi, a), "-")

    def group(self):
        """

        convert
        δ[q1, a] = q2; δ[q1, b] = q3; δ[q1, c] = q4

        to
        δ[q1] = (q2, q3, q4)

        """

        new_dict = {}
        for key, val in self.items():
            new_dict.setdefault(key[0], tuple())
            new_dict[key[0]] = new_dict[key[0]] + (val,)
        return new_dict

    def toNode(self, qi):
        """
        get a list of transitions (q, a) that siffice δ[q, a] == qi
        """
        return Set((p, a) for (p, a), q in self.items() for q2 in q if q2 == qi)

    def fromNode(self, qi):
        """
        get a list of transitions (q, a) that siffice δ[qi, a]
        """
        return Set((p, a) for (p, a), q in self.items() if p == qi)


class ô(δ):
    """

    extended δ function
    accepts δ[q, wa]
    as well as original δ[q, w]

    """

    def __getitem__(self, key):
        qi, word = key

        if len(word) == 1:
            return super().__getitem__(key)

        # ô(q, w) is defined
        rec = self.__getitem__((qi, word[:-1]))
        if rec and rec != "-":
            # δ(ô(q, w)) is defined
            last = super().__getitem__((rec, word[-1]))
            if last:
                # δ(ô(q, w))
                return last
        # else None

    def __setitem__(self, key, value):
        qi, word = key

        if len(word) == 1:
            return super().__setitem__(key, value)

        if self.__getitem__((qi, word[:-1])):
            super().__setitem__((qi, word[-1]), value)
