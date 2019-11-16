from dfa import *
from nfa import *

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
Q = range(1, 5 + 1)
Σ = {"a", "b", "c", "d"}
δ = NDTransitionFunction(Σ, epsilon=False)
δ[1] = None, 4, None, 1
δ[2] = None, 4, (2, 5), None
δ[3] = 1, (1, 3), (1, 2), (1, 2)
δ[4] = None, (3, 4), None, None
δ[5] = 4, (1, 4), 4, None
A = NFA(Q, Σ, δ, 2, {4})
B = A.toDFA()
B.table()
B.diagram()


Q = range(1, 4)
Σ = {"F", "G", "D"}
δ = DTransitionFunction(Σ)
A = DFA(Q, Σ, δ, 1, {2})

δ[1, "F"] = 2
δ[2, "G"] = 3
"""

"""
δ[1, "F"] = 2
δ[1, "G"] = 2
to
δ[1, "F+G"] = 2
"""

"""
δ[1, "F"] = 2
δ[2, "G"] = 3
to
δ[1, "F.G"] = 3
"""

"""
δ[1, "F"] = 2
δ[2, "E"] = 2
δ[2, "G"] = 3

δ[1, "F.E*.G"] = 3
"""
"""
A.toRE()
A.diagram()
"""
