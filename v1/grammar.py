

class Grammar(dict):
    def __setitem__(self, key, value):
        if isinstance(value, str):
            # δ["S"] = "aS | bA | c"
            values = list(map(str.strip, value.split("|")))
            for value in values:
                if not (0 < len(value) <= 2):
                    raise NotImplementedError("invalid grammar?")
            super().__setitem__(str(key), values)

    def table(self):
        print()
        print("-" * 50)
        print("|" + ("REGULAR GRAMMAR").center(48) + "|")
        print("-" * 50)

        print("\n+" + "-" * 30 + "+")
        for source in self:
            print("| " + (source + " -> " +
                          " | ".join(self[source])).ljust(28) + " |")
        print("+" + "-" * 30 + "+")

        print("start state: S")
        print()

    def toDFA(self):
        """
        1. convert all rules S -> aT to S (->a) T
        2. convert all rules U -> a  to U (->a) ((qf))
        """
        from nfa import NFA, NDTransitionFunction

        def getAlphabet():
            return {path[0] for key in self for path in self[key]}

        Q = list(self)

        δ = NDTransitionFunction(getAlphabet())
        for source in self:
            for path in self[source]:
                letter, *target = tuple(path)

                if target:
                    δ[source, letter] = target[0]
                else:
                    δ[source, letter] = "qf"
                    if "qf" not in Q:
                        Q.append("qf")

        return NFA(Q, getAlphabet(), δ, "S", {"qf"})
