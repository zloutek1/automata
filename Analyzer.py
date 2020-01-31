from PDA import PDA

from utils import Set, Stack


class TopDownAnalyzer(PDA):
    pass


class BottomUpAnalyzer(PDA):
    def __init__(self, Q, Σ, Γ, ô, q0, Z0, F):
        super().__init__(Q, Σ, Γ, ô, q0, Z0, F)
        self.ô = ô
        del self.δ

    def analyze(self, word):
        word = Stack(*reversed(word))
        qi = self.q0
        stack = Stack(self.Z0)

        memory = [(qi, word, stack)]

        depth = 0
        new_memory = []

        for (qi, word, stack) in memory:
            possibleRules = list(filter(lambda rule:
                                        rule[0] == qi and
                                        rule[1] in (word.top(), 'ε') and
                                        rule[2] in (stack[:len(rule[1])], 'ε'), self.ô))

            print(qi, word.reverse(), stack.reverse())
            print(possibleRules)
