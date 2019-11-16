from utils import Set
import FA
import DFA
import NFA
import EFA
import RE
import CFG
import G


def test_dfa():
    δ = DFA.δ()
    A = DFA(Set(1, 2, 3, 4, 5, 6, 7), Set("a", "b"), δ, 1, Set(3, 5, 6))

    δ[1, "a", "b"] = 2, "-"
    δ[2, "a", "b"] = 3, 4
    δ[3, "a", "b"] = 6, 5
    δ[4, "a", "b"] = 3, 2
    δ[5, "a", "b"] = 6, 3
    δ[6, "a", "b"] = 2, "-"
    δ[7, "a", "b"] = 6, 1

    # A.table()
    B = A.minimize()
    # B.table()

    ######################################################################

    δ = DFA.δ()
    A = DFA(Set("r1", "r2", "p", "q1", "q2"), Set(
        "F1", "F2", "E", "G1", "G2"), δ, "r1", Set("q2"))

    δ["r1", "F1"] = "p"
    δ["r2", "F2"] = "p"
    δ["p", "E"] = "p"
    δ["p", "G1"] = "q1"
    δ["p", "G2"] = "q2"

    A.diagram()
    B = A.toRE()
    B.diagram()


def test_nfa():
    δ = NFA.δ()
    A = NFA(Set(1, 2, 3, 4, 5), Set("a", "b", "c", "d"), δ, 2, Set(4))

    δ[1, "a", "b", "c", "d"] = Set(), Set(4), Set(), Set(1)
    δ[2, "a", "b", "c", "d"] = Set(), Set(4), Set(2, 5), Set()
    δ[3, "a", "b", "c", "d"] = Set(1), Set(1, 3), Set(1, 2), Set(1, 2)
    δ[4, "a", "b", "c", "d"] = Set(), Set(3, 4), Set(), Set()
    δ[5, "a", "b", "c", "d"] = Set(4), Set(1, 4), Set(4), Set()

    B = A.toDFA()
    # B.table()


def test_efa():
    δ = EFA.δ()
    A = EFA(Set(0, 1, 2, 3, 4), Set("a", "b", "c", "d"), δ, 0, Set(2))

    δ[0, "a", "b", "c", "d", "ε"] = Set(), Set(), Set(), Set(), Set(1)
    δ[1, "a", "b", "c", "d", "ε"] = Set(0), Set(), Set(), Set(3), Set(2)
    δ[2, "a", "b", "c", "d", "ε"] = Set(3), Set(), Set(), Set(), Set()
    δ[3, "a", "b", "c", "d", "ε"] = Set(), Set(), Set(), Set(4), Set(4)
    δ[4, "a", "b", "c", "d", "ε"] = Set(), Set(3), Set(2), Set(), Set()

    B = A.toNFA()
    C = A.toDFA()
    # B.table()


def test_re():
    δ = RE.δ()
    A = RE(Set(0, 1), Set(), δ, Set(0), Set(1))
    δ[0, "a.((a+b)*+c).d"] = 1
    B = A.toEFA()
    # B.diagram()


def test_grammar():
    P = G.P({
        "S": "aA | bC | a | ε",
        "A": "bB | aA | b | c",
        "B": "aB | bC | aC | cA | c",
        "C": "a | b | aA | bB"
    })
    A = G(Set("S", "A", "C", "B"), Set("a", "b", "c"), P, "S")
    B = A.toNFA()
    # B.table()


def test_cfg():
    P = CFG.P({
        "A": "Bd | c",
        "B": "Bdd | Ccc | aCd",
        "C": "Aa"
    })
    A = CFG(Set("A", "B", "C"), Set("a", "b", "c", "d"), P, "A")
    A.Ne()


def test():
    simpleregex = "3+(4+(5+[6+(7+8)+9]+10)+11)+12"
    A = EFA.EFA.fromRegex(simpleregex)
    print(A)
    A.diagram()


test_dfa()
test_nfa()
test_efa()
test_re()
test_grammar()
test_cfg()
# test()
