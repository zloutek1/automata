from utils import Set, Rule
import FA
import DFA
import NFA
import EFA
import RE
import CFG
import G
import PDA


def test_dfa():
    δ = DFA.δ()
    A = DFA(Set(1, 2, 3, 4, 5, 6, 7), Set("a", "b"), δ, 1, Set(3, 5, 6))

    δ[1, "a"] = 2; δ[1, "b"] = "-"
    δ[2, "a"] = 3; δ[2, "b"] = 4
    δ[3, "a"] = 6; δ[3, "b"] = 5
    δ[4, "a"] = 3; δ[4, "b"] = 2
    δ[5, "a"] = 6; δ[5, "b"] = 3
    δ[6, "a"] = 2; δ[6, "b"] = "-"
    δ[7, "a"] = 6; δ[7, "b"] = 1

    # A.table()
    B = A.minimize()
    B.diagram()
    # B.table()


def test_nfa():
    δ = NFA.δ()
    A = NFA(Set(1, 2, 3, 4, 5), Set("a", "b", "c", "d"), δ, 2, Set(4))

    δ[1, "a", "b", "c", "d"] = Set(), Set(4), Set(), Set(1)
    δ[2, "a", "b", "c", "d"] = Set(), Set(4), Set(2, 5), Set()
    δ[3, "a", "b", "c", "d"] = Set(1), Set(1, 3), Set(1, 2), Set(1, 2)
    δ[4, "a", "b", "c", "d"] = Set(), Set(3, 4), Set(), Set()
    δ[5, "a", "b", "c", "d"] = Set(4), Set(1, 4), Set(4), Set()

    # A.table()
    B = A.toDFA()
    B.diagram()
    # B.table()


def test_efa():
    δ = EFA.δ()
    A = EFA(Set(0, 1, 2, 3, 4), Set("a", "b", "c", "d"), δ, 0, Set(2))

    δ[0, "a", "b", "c", "d", "ε"] = Set(), Set(), Set(), Set(), Set(1)
    δ[1, "a", "b", "c", "d", "ε"] = Set(0), Set(), Set(), Set(3), Set(2)
    δ[2, "a", "b", "c", "d", "ε"] = Set(3), Set(), Set(), Set(), Set()
    δ[3, "a", "b", "c", "d", "ε"] = Set(), Set(), Set(), Set(4), Set(4)
    δ[4, "a", "b", "c", "d", "ε"] = Set(), Set(3), Set(2), Set(), Set()

    # A.table()
    B = A.toNFA()
    C = A.toDFA()
    # B.table()
    # C.table()


def test_re():
    δ = RE.δ()
    A = RE(Set(0, 1), Set(), δ, Set(0), Set(1))
    δ[0, "a.((a+b)*+c).d"] = Set(1)
    B = A.toEFA()
    B.diagram()


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
        "S": "aA | bB",
        "A": "aAB | aa | AC | AE",
        "B": "bBA | bb | CB | BF",
        "C": "DE",
        "D": "cc | DD",
        "E": "FF | FE",
        "F": "EcE"
    })
    A = CFG(Set("S", "A", "B", "C", "D", "E", "F"), Set("a", "b", "c"), P, "S")

    B = A.reduce()

    ######################################################################

    P = CFG.P({
        "S": "ABC",
        "A": "Ab | BC",
        "B": "bB | b | Ab | ε",
        "C": "cD | c | Ac | ε",
        "D": "SSD | cSAc"
    })
    A = CFG(Set("S", "A", "B", "C", "D"), Set("b", "c"), P, "S")
    B = A.remove_ε()

    ######################################################################

    P = CFG.P({
        "S": "X | Y",
        "A": "bS | D",
        "D": "bA",
        "B": "Sa | a",
        "X": "aAS | C",
        "C": "aD | S",
        "Y": "SBb"
    })
    A = CFG(Set("S", "A", "B", "C", "D", "X", "Y"), Set("a", "b"), P, "S")
    B = A.remove_primitive_rules()

    ######################################################################

    P = CFG.P({
        "S": "SaSbS | aAa | bBb",
        "A": "aA | aaa | B | ε",
        "B": "Bb | bb | b"
    })
    A = CFG(Set("S", "A", "B"), Set("a", "b"), P, "S")
    B = A.toOwn()
    C = B.toCNF()

    ######################################################################

    P = CFG.P({
        "S": "YZ | aXZa",
        "X": "YX | bY | aYZ",
        "Y": "ε | c | YZ",
        "Z": "a | Xb | ε | c"
    })
    G1 = CFG(Set("S", "X", "Y", "Z"), Set("a", "b", "c"), P, "S")
    G1_1 = G1.remove_ε()
    G1_2 = G1_1.remove_primitive_rules()
    # print("---[ G1 ]---")
    # print(G1, end="\n" * 3)
    # print(G1.Nε, end="\n" * 3)
    # print(G1_1, end="\n" * 3)
    # print(G1_1.NS, G1_1.NX, G1_1.NY, G1_1.NZ, end="\n" * 3)
    # print(G1_2, end="\n" * 3)

    P = CFG.P({
        "S": "Aa | a | Eb | abbc | aDD",
        "A": "Aab | b | SEE | baD",
        "B": "DaS | BaaC | a",
        "C": "Da | a | bB | Db | SaD",
        "D": "Da | DBc | bDb | DEaD",
        "E": "Aa | a | bca"
    })
    G2 = CFG(Set("S", "A", "B", "C", "D", "E"), Set("a", "b", "c"), P, "S")
    G2_1 = G2.toOwn()
    G2_2 = G2.toCNF()
    # print("---[ G2 ]---")
    # print(G2, end="\n" * 3)
    # print("Nε=", G2.Nε, " NA={", G2.NS, G2.NA,
    #       G2.NB, G2.NC, G2.ND, G2.NE, "} V=", G2.V)
    # print(G2_1, end="\n" * 3)
    # print(G2_2, end="\n" * 3)

    P = CFG.P({
        "S": "Xc | Yd | Yb",
        "X": "Xb | a",
        "Y": "SaS | Xa"
    })
    G = CFG(Set("S", "X", "Y"), Set("a", "b", "c", "d"), P, "S")
    G1 = G.remove_left_recursion()
    G2 = G1.toGNF()

    P = CFG.P({
        "S": "ε | abSA",
        "A": "AaB | aB | a",
        "B": "aSS | bA | aB"
    })
    G = CFG(Set("S", "A", "B"), Set("a", "b"), P, "S")
    # M = G.toTopDownAnalyzer()
    # N = G.toBottomUpAnalyzer()
    # print(N.analyze("ababaa"))


def test_pda():
    δ = PDA.δ()
    M = PDA(Set("q0"), Set("a", "b"), Set("Z", "A"), δ, "q0", "Z", Set())
    δ["q0", "a", "Z"] = Set(("q0", "A"))
    δ["q0", "a", "A"] = Set(("q0", "AA"))
    δ["q0", "b", "A"] = Set(("q0", "ε"))


def test():
    print(Rule("SaSaS").chars)
    print(Rule("aX'b").chars)
    print(Rule("ab̄c").chars)
    print(Rule("ab̂c").chars)
    print(Rule("a<bc<d>f>e").chars)


test_dfa()
test_nfa()
test_efa()
test_re()
test_grammar()
test_cfg()
test_pda()

# test()
