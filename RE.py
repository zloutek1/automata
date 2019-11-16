import sys
import types
from dataclasses import dataclass

from utils import Set, parseRegex
import FA


class RE(FA.FA):
    def __init__(self, Q, Σ, δ, I, F):
        """

        I  : I ⊆ Q set of initial states

        """
        super().__init__(Q, Σ, δ, I, F)

    def toEFA(self):
        """

        (a) remove all edges valued Ø
        (b) convert any edge p →E q
            F + G into p →F,G q
            F.G into p →F s →G q
            F* into p →ε ⟲F s →ε q

        """
        import EFA

        def toAST(tokens):
            stack = []
            for token in tokens:
                if token.name == "CHAR":
                    stack.append(Literal(token.value))

                elif token.name == "ALT":
                    right, left = stack.pop(), stack.pop()
                    stack.append(Or(left, right))

                elif token.name == "CONCAT":
                    right, left = stack.pop(), stack.pop()
                    stack.append(Then(left, right))

                elif token.name == "STAR":
                    left = stack.pop()
                    stack.append(Star(left))

                else:
                    raise NotImplementedError(f"Regex unknown token {token}")

            if len(stack) != 1:
                raise NotImplementedError(
                    f"Stack must be of length 1, is {len(stack)}")

            return stack[0]
        """
        for (qi, a) in self.δ:
            print(regexp_to_postfix(a))
        """

        δ = EFA.δ(Q=self.Q, Σ=self.Σ)
        efa = EFA(self.Q, self.Σ, δ, "START", Set("END"))

        for qs in self.I:
            δ["START", "ε"] = qs

        for qf in self.F:
            δ[qf, "ε"].add("END")

        for (qfrom, a), qto in self.δ.items():
            tokens = parseRegex(a)
            ast = toAST(tokens)
            ast.eval(efa, qfrom, qto)

        return efa


class δ(FA.δ):
    pass


@dataclass
class Epsilon:
    pass

    def eval(self, efa, qfrom, qto):
        return "ε"

    def __repr__(self):
        return "ε"


@dataclass
class Literal:
    value: str

    def eval(self, efa, qfrom, qto):
        return self.value

    def __repr__(self):
        return f"{self.value}"


@dataclass
class Or:
    left: None
    right: None

    def eval(self, efa, qfrom, qto):
        if type(self.left) in (Epsilon, Literal):
            efa.δ[qfrom, self.left].add(qto)
        if type(self.right) in (Epsilon, Literal):
            efa.δ[qfrom, self.right].add(qto)

        self.left.eval(efa, qfrom, qto)
        self.right.eval(efa, qfrom, qto)

    def __repr__(self):
        return f"({self.left}|{self.right})"


@dataclass
class Then:
    left: None
    right: None

    def eval(self, efa, qfrom, qto):
        s = f"({qfrom}.{qto})"

        if type(self.left) in (Epsilon, Literal):
            efa.δ[qfrom, self.left].add(s)
        if type(self.right) in (Epsilon, Literal):
            efa.δ[s, self.right].add(qto)

        self.left.eval(efa, qfrom, s)
        self.right.eval(efa, s, qto)

    def __repr__(self):
        return f"({self.left}.{self.right})"


@dataclass
class Star:
    left: None

    def eval(self, efa, qfrom, qto):
        s = f"ε.({self.left})*.ε"

        efa.δ[qfrom, "ε"].add(s)
        if type(self.left) in (Epsilon, Literal):
            efa.δ[s, self.left].add(s)
        efa.δ[s, "ε"].add(qto)

        self.left.eval(efa, s, s)

    def __repr__(self):
        return f"({self.left})*"


class call(types.ModuleType):
    """
    make the module callable simplifying
    from RE import RE
    to
    import RE
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return RE(*args, **kwargs)


sys.modules[__name__] = call()
