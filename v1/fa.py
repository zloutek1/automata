def roman(num):
    """ Convert an integer to a Roman numeral. """
    if not 0 < num < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC',
            'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []
    for i in range(len(ints)):
        count = int(num / ints[i])
        result.append(nums[i] * count)
        num -= ints[i] * count
    return ''.join(result)


class FA:
    """ Finite Automata """

    def __init__(self, Q, Σ, δ, q0, F):
        """
        Q: states
        Σ: alphabet
        δ: transition function
        q0: initial state
        F: accepted states
        """

        self.states = list(Q)
        self.alphabet = sorted(Σ)
        self.func = δ
        self.initial_state = q0
        self.accepted_sates = F

    @property
    def isDeterministic(self):
        from dfa import DTransitionFunction
        return isinstance(self.func, DTransitionFunction)

    def print_header(self):
        print("-" * 50)
        print("|" + (("DETERMINISTIC" if self.isDeterministic() else "NON-TETERMINISTIC") +
                     "FINITE AUTOMATA").center(48) + "|")
        print("-" * 50)

    def table(self, table_body):
        print()
        print("states:", self.states)
        print("alphabet:", self.alphabet)
        print("Transition table:")

        table_body()

        print("start state:", self.initial_state)
        print("accepted states:", self.accepted_sates)
        print()

    def diagram(self, filename=None, *, transition=None):
        import graphviz as gv
        transition = transition if transition else self.func
        G = gv.Digraph('finite_state_machine', format="png")
        G.attr(rankdir='LR', size='8,5')

        G.attr('node', shape='point')
        G.node("")
        G.attr('node', shape='circle')
        G.edge("", str(self.initial_state), label="")

        G.attr('node', shape='doublecircle')
        for state in self.accepted_sates:
            G.node(str(state))

        if self.isDeterministic:
            G.attr('node', shape='circle')
            for i in transition:
                target = str(transition.get(i))
                initial = str(i[0])
                value = str(i[1])
                if target != "":
                    G.edge(initial, target, label=value)

            filename = "dfa" if filename is None else filename
            G.render(filename, view=False)

        else:
            G.attr('node', shape='circle')
            for i in transition:
                targets = transition.get(i)
                initial = str(i[0])
                value = str(i[1])
                for target in targets:
                    G.edge(initial, str(target), label=value)

            filename = "nfa" if filename is None else filename
            G.render(filename, view=False)
