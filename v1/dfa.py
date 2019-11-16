from fa import *


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

    def normalize(self, step=0, minimalize_until=None):
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

        if step == 1:
            return self

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

        if step == 2:
            return self

        min_dfs = self.minimalize(minimalize_until=minimalize_until)

        if step == 3:
            return min_dfs

        return self.rename(min_dfs)

    @staticmethod
    def rename(dfs):
        # order and rename
        new_δ = DTransitionFunction(dfs.alphabet)
        letterMapping = {}
        states = [dfs.initial_state]
        index = 0

        while index < len(states):
            letterMapping[states[index]] = letterMapping.get(states[index],
                                                             chr(ord('A') + len(letterMapping)))
            for letter in dfs.alphabet:
                value = dfs.func.get((states[index], letter))

                letterMapping[value] = letterMapping.get(value,
                                                         chr(ord('A') + len(letterMapping)))

                if value not in states:
                    states.append(value)

                new_δ[letterMapping[states[index]],
                      letter] = letterMapping[value]

            index += 1

        new_states = list(letterMapping.values())
        new_accepting = {letterMapping[state]
                         for state in dfs.accepted_sates}

        return DFA(new_states, dfs.alphabet, new_δ, new_states[0], new_accepting)

    def minimalize(self, step=0, minimalize_until=None, groups=None, func=None):
        """
        1. iteration:
            separate into two groups (non-accepting, accepting)
            assign to each transition value cooresponding to target's group
        n+1th iteration:
            separate into groups with different transition paths
            assign to each transition value cooresponding to target's group
        repeat until not change happened
        """

        if minimalize_until == step - 1:
            groups = {group: [key for key in groups if groups[key] == group]
                      for group in groups.values()}
            states = sum(groups.values(), [])

            return DFA(states, self.alphabet, func, self.initial_state, self.accepted_sates)

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

            return self.minimalize(step + 1, minimalize_until, groups, func)

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
            return self.minimalize(step + 1, minimalize_until, new_groups, new_func)

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

    def toRE(self):
        from regular import RETransitionFunction

        δ = RETransitionFunction(self.alphabet, self.func)

        δ["x", "\e"] = self.initial_state
        for accepted_sate in self.accepted_sates:
            δ[accepted_sate, "\e"] = "y"

        # get reachables
        index = 0
        reachable = ["x"]
        while index < len(reachable):
            for letter in self.alphabet + ["\e"]:
                item = δ.get((reachable[index], letter))
                if item not in reachable and item is not None:
                    reachable.append(item)
            index += 1

        # get unreachables
        not_reachable = set(self.states) - set(reachable)

        for state in not_reachable:
            self.states.remove(state)
            for letter in self.alphabet:
                if (state, letter) in δ:
                    del δ[state, letter]

        for state in self.states:
            to_state = [path for path in δ if δ[path] == state]
            from_state = [path for path in δ if path[0] == state]

            for r in list(to_state):
                for q in list(from_state):
                    if r in δ:
                        del δ[r]
                    δ[r[0], f"{r[1]}.{q[1]}"] = δ[q]
                    if q in δ:
                        del δ[q]

        print(δ)


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
