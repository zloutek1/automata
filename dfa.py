def symbols(syms):
    globals().update({sym: sym for sym in syms.split()})
    return [sym for sym in syms.split()]


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


class DFA(FA):
    """ Deterministic Finite Autoamata"""

    def get_width(self, i):
        """ return with of i'th column """
        return max(map(len, map(str, self.states))) if i == 0 else max(map(lambda key: len(str(self.func[key])), filter(lambda key: key[1] == self.alphabet[i - 1], self.func.keys())))

    def sep(self):
        """ print +---+---+---+ separation of the table """
        print("+-" + "-" * self.get_width(0) + "-+-" + "-+-".join("-" * self.get_width(i + 1)
                                                                  for i, letter in enumerate(self.alphabet)) + "-+")

    def table_body(self):
        """ print | node | transition1 | transition2 | ... | for each state """
        self.sep()
        print("| " + " " * self.get_width(0) + " | " + " | ".join(str(letter).rjust(self.get_width(i + 1))
                                                                  for i, letter in enumerate(self.alphabet)) + " |")
        self.sep()
        for state in self.states:
            print("| " + str(state).rjust(self.get_width(0)) + " | " + " | ".join(str(self.func.get((state, letter), "")).rjust(self.get_width(i + 1))
                                                                                  for i, letter in enumerate(self.alphabet)) + " |")
        self.sep()

    def table(self):
        super().table(self.table_body)

    def normalize(self):
        """
        1. add hell if necessary
        2. remove unreachable nodes
        3. start minimalizing
        4. order properly
        """

        # add hell
        hell_index = len(self.func.group().keys()) + 1
        items = list(self.func.items())
        for key, value in items:
            if value == "":
                if hell_index not in self.states:
                    self.states.append(hell_index)
                    self.func[hell_index] = tuple(
                        hell_index for i in self.alphabet)
                self.func[key] = hell_index

        # get reachables
        index = 0
        reachable = [self.initial_state]
        while index < len(reachable):
            for letter in self.alphabet:
                item = self.func[reachable[index], letter]
                if item not in reachable:
                    reachable.append(item)
            index += 1

        # get unreachables
        not_reachable = set(self.states) - set(reachable)
        for state in not_reachable:
            self.states.remove(state)
            for letter in self.alphabet:
                del self.func[state, letter]

        min_dfs = self.minimalize()

        # order and rename
        new_δ = DTransitionFunction(self.alphabet)
        letterMapping = {}
        states = [min_dfs.initial_state]
        index = 0

        while index < len(states):
            letterMapping[states[index]] = letterMapping.get(states[index],
                                                             chr(ord('A') + len(letterMapping)))
            for letter in self.alphabet:
                value = min_dfs.func.get((states[index], letter))

                letterMapping[value] = letterMapping.get(value,
                                                         chr(ord('A') + len(letterMapping)))

                if value not in states:
                    states.append(value)

                new_δ[letterMapping[states[index]],
                      letter] = letterMapping[value]

            index += 1

        new_states = list(letterMapping.values())
        new_accepting = {letterMapping[state]
                         for state in min_dfs.accepted_sates}
        return DFA(new_states, min_dfs.alphabet, new_δ, new_states[0], new_accepting)

    def minimalize(self, step=0, groups=None, func=None):
        """
        1. iteration:
            separate into two groups (non-accepting, accepting)
            assign to each transition value cooresponding to target's group
        n+1th iteration:
            separate into groups with different transition paths
            assign to each transition value cooresponding to target's group
        repeat until not change happened
        """

        if step == 0:
            groups = {
                state: roman(
                    1) if state not in self.accepted_sates else roman(2)
                for state in self.states
            }

            func = DTransitionFunction(self.alphabet)
            for state in self.states:
                for letter in self.alphabet:
                    func[state, letter] = groups.get(self.func[state, letter])

            return self.minimalize(step + 1, groups, func)

        new_groups = {}
        force_move = 0
        numeratd_patterns = []
        for i in range(len(set(groups.values()))):
            for state, val in groups.items():
                if val == roman(i + 1):
                    if func.group()[state] not in numeratd_patterns:
                        numeratd_patterns.append(func.group()[state])
                    index = numeratd_patterns.index(func.group()[state])
                    new_groups[state] = roman(index + 1 + force_move)
            force_move += len(numeratd_patterns)
            numeratd_patterns = []

        new_func = DTransitionFunction(self.alphabet)
        for state in self.states:
            for letter in self.alphabet:
                new_func[state, letter] = new_groups.get(
                    self.func[state, letter])

        if groups != new_groups and func != new_func:
            return self.minimalize(step + 1, new_groups, new_func)

        ##
        # construct final automata
        new_Q = {}
        for state, key in groups.items():
            new_Q.setdefault(key, [])
            new_Q[key].append(state)

        new_δ = DTransitionFunction(self.alphabet)
        for state, val in func.group().items():
            firsts = list(map(lambda val: val[0], new_Q.values()))
            if state in firsts:
                state = list(new_Q.keys())[firsts.index(state)]
                new_δ[state] = val

        new_initial = list(new_Q.keys())[list(
            map(lambda val: self.initial_state in val, new_Q.values())).index(True)]
        new_accepting = set([list(new_Q.keys())[list(
            map(lambda val: accepting_state in val, new_Q.values())).index(True)]
            for accepting_state in self.accepted_sates])

        return DFA(new_Q, self.alphabet, new_δ, new_initial, new_accepting)


class NFA(FA):
    def __init__(self, Q, Σ, δ, q0, F):
        super().__init__(Q, Σ, δ, q0, F)
        self.alphabet = sorted(Σ) + (['Ɛ'] if δ.epsilon else [])

    def De(self, state):
        if not self.func.epsilon:
            raise NotImplementedError()

        reachable = [state]
        for state in reachable:
            for s in self.func.get((state, 'Ɛ'), []):
                if s not in reachable:
                    reachable.append(s)

        return set(reachable)

    def get_width(self, i):
        """ return with of i'th column """
        return (max(map(len, map(str, self.states)))
                if i == 0 else
                max(map(
                    lambda key: len(str(self.func[key])),
                    filter(
                        lambda key: key[1] == self.alphabet[i - 1],
                        self.func.keys())
                ))
                if not (self.func.epsilon and i == len(self.alphabet) - 1) else
                max(map(len, [str(self.De(state)) for state in self.states]))
                )

    def sep(self):
        """ print +---+---+---+ separation of the table """
        print("+-" + "-" * self.get_width(0) + "-+-" +
              "-+-".join("-" * self.get_width(i + 1)
                         for i, letter in enumerate(self.alphabet)) +
              "-+" + ("" if not self.func.epsilon else "-" + "-" * self.get_width(len(self.alphabet) - 1) + "-+"))

    def table_body(self):
        """ print | node | transition1 | transition2 | ... | for each state """
        self.sep()
        print("| " + " " * self.get_width(0) + " | " +
              " | ".join(str(letter).rjust(self.get_width(i + 1))
                         for i, letter in enumerate(self.alphabet)) + " |" +
              ("" if not self.func.epsilon else " " + "De".rjust(self.get_width(len(self.alphabet) - 1)) + " |"))
        self.sep()
        for state in self.states:
            print("| " + str(state).rjust(self.get_width(0)) + " | " +
                  " | ".join(str(self.func.get((state, letter), "Ø")).rjust(self.get_width(i + 1))
                             for i, letter in enumerate(self.alphabet)) + " |" +
                  ("" if not self.func.epsilon else (" " + str(self.De(state))).rjust(self.get_width(len(self.alphabet) - 1) + 1) + " |"))
        self.sep()

    def table(self):
        super().table(self.table_body)

    def toDFA(self):
        if self.func.epsilon:
            return self.toNFA().toDFA()

        def rename_state(state):
            import re
            return re.sub(r"[\{\}\,\s]", r"", f"[{state}]")

        dfa_δ = DTransitionFunction(self.alphabet)
        states = [set([self.initial_state])]
        index = 0

        while index < len(states):
            for letter in self.alphabet:
                res = set()
                for state in states[index]:
                    res = res | self.func.get((state, letter), set())

                state_name = str(states[index]) if len(
                    states[index]) != 0 else 'Ø'
                dfa_δ[state_name, letter] = str(res) if len(res) != 0 else 'Ø'
                if res not in states:
                    states.append(res)
            index += 1

        seen = set()
        Q = [rename_state(key[0]) for key in dfa_δ]
        Q = [state for state in Q if not (state in seen or seen.add(state))]

        δ = DTransitionFunction(
            self.alphabet, {(rename_state(key[0]), key[1]): rename_state(value) for key, value in dfa_δ.items()})

        initial_state = Q[Q.index(f"[{self.initial_state}]")]
        accepted_sates = set(rename_state(state)
                             for accepting in self.accepted_sates
                             for state in states
                             if accepting in state)

        return DFA(Q, self.alphabet, δ, initial_state, accepted_sates)

    def toNFA(self):
        if not self.func.epsilon:
            return self

        nfa_δ = NDTransitionFunction(self.alphabet)

        for state in self.states:
            for letter in self.alphabet:
                if letter == "Ɛ":
                    continue

                step1 = self.func.get((state, letter), set())

                step2 = set()
                for s in self.De(state):
                    step2 |= self.func.get((s, letter), set())

                step3 = set()
                for s in step1 | step2:
                    step3 |= self.De(s)

                nfa_δ[state, letter] = tuple(step3)

        alphabet = [letter for letter in self.alphabet if letter != 'Ɛ']
        accepted_sates = set([self.initial_state]
                             if any([state in self.De(self.initial_state) for state in self.accepted_sates]) else
                             []) | self.accepted_sates

        return NFA(self.states, alphabet, nfa_δ, self.initial_state, accepted_sates)


class DTransitionFunction(dict):
    """ Deterministic Transition Function """

    def __init__(self, Σ, *args, **kwargs):
        self.alphabet = sorted(Σ)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 2:
            # δ[1, "a"] = 1
            value = value if value is not None else ""
            super().__setitem__(key, value)
            return

        if isinstance(key, tuple) and len(key) == len(value) + 1:
            # δ[1, "a", "b"] = (1, 2)
            for k, v in zip(key[1:], value):
                self.__setitem__((key[0], k), v)
            return

        if not isinstance(key, tuple) and isinstance(value, tuple) and len(value) == len(self.alphabet):
            # δ[1] = (1, 2)
            for k, v in zip(self.alphabet, value):
                self.__setitem__((key, k), v)
            return

        raise NotImplementedError()

    def group(self):
        """
        group δ[1, "a"] = 2; δ[1, "b"] = 3
        into δ[1] = (2, 3)
        """

        new_dict = {}
        for key, val in self.items():
            new_dict.setdefault(key[0], tuple())
            new_dict[key[0]] = new_dict[key[0]] + (val,)
        return DTransitionFunction(self.alphabet, new_dict)


class NDTransitionFunction(dict):
    """ Non Determinisitc Transition Function """

    def __init__(self, Σ, epsilon=False, *args, **kwargs):
        self.alphabet = sorted(Σ)
        self.epsilon = epsilon
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        eps = ['Ɛ'] if self.epsilon else []

        if isinstance(key, tuple) and len(key) == 2 and isinstance(value, tuple):
            # δ[1, "a"] = 1, 3
            for val in value:
                self.__setitem__(key, val)
            return

        if isinstance(key, tuple) and len(key) == 2:
            # δ[1, "a"] = 1; δ[1, "a"] = 2
            if value is not None:
                super().setdefault(key, set())
                super().__getitem__(key).add(value)
            return

        if isinstance(key, tuple) and isinstance(value, tuple) and len(key) == len(value) + 1 + len(eps):
            # δ[1, "a", "b"] = (1, 2), 3
            for k, v in zip(key[1:], value):
                self.__setitem__((key[0], k), v)
            return

        if not isinstance(key, tuple) and isinstance(value, tuple) and len(value) == len(self.alphabet) + len(eps):
            for k, v in zip(self.alphabet + eps, value):
                self.__setitem__((key, k), v)
            return

        raise NotImplementedError()


"""
Q = range(1, 13)
Σ = {"a", "b"}
δ = DTransitionFunction(Σ)
A = DFA(Q, Σ, δ, 2, {4, 7})
δ[1] = 3, 1
δ[2] = 9, 4
δ[3] = None, 1
δ[4] = 9, 4
δ[5] = 8, 5
δ[6] = 5, 4
δ[7] = 6, 9
δ[8] = 11, None
δ[9] = 7, 9
δ[10] = 12, 3
δ[11] = 8, 1
δ[12] = None, 10

A.table()
A.diagram()
B = A.normalize()
B.table()
B.diagram()
"""

"""
Q = range(0, 4 + 1)
Σ = {"a", "b", "c", "d"}
δ = NDTransitionFunction(Σ, epsilon=True)
δ[0] = None, None, None, None, 1
δ[1] = 0, None, None, 3, 2
δ[2] = 3, None, None, None, None
δ[3] = None, None, None, 4, 4
δ[4] = None, 3, 2, None, None
A = NFA(Q, Σ, δ, 0, {2})
B = A.toNFA()
B.table()
B.diagram()
"""

Q = range(1, 10 + 1)
Σ = {"a", "b"}
δ = DTransitionFunction(Σ)
A = DFA(Q, Σ, δ, 5, {2, 6})
δ[1] = 4, 1
δ[2] = 8, 8
δ[3] = 4, 3
δ[4] = 2, 6
δ[5] = 2, 6
δ[6] = 3, 3
δ[7] = 4, 3
δ[8] = 10, 3
δ[9] = 3, 6
δ[10] = 10, 1
A.table()
A.diagram()
B = A.normalize()
B.table()
B.diagram()
