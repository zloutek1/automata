from fa import *


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
        from dfa import DFA, DTransitionFunction

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

    def toGrammar(self):
        from grammar import Grammar

        """
        1. δ(q, a)          => Q -> aP
        2. δ(q, a); q in P  => Q - a
        3. δ(q0, a)         => S -> aP
        4. δ(q0, a)         => S -> aP
        5. q0 in F          ....
        """
        grammar_rules = {}

        for path in self.func:
            source, letter = path
            targets = self.func[path]

            source = source if source is not self.initial_state else "S"
            grammar_rules.setdefault(source, "")

            for target in targets:
                target = target if target is not self.initial_state else "S"

                if source in self.accepted_sates:
                    grammar_rules[source] += (f"| {letter}")
                elif source is self.initial_state:
                    grammar_rules[source] += (f"| {letter}{target}")
                else:
                    grammar_rules[source] += (f"| {letter}{target}")

            grammar_rules[source] = grammar_rules[source].strip("|").strip()

        g = Grammar()
        for source, rule in grammar_rules.items():
            g[source] = rule
        return g


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
