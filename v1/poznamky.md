
# prevod Regularneho prechodoveho grafu -> NFA s eps

1. odstranime viac vstupnych stavov
    + ak ma viac vstupnych stavov
    + pridame vstupny vrchol a \eps kroky do kazdeho povodneho vstupneho

2. odstran vsetky hrany s Ø

3. preved hrany
    + F + G => -> F,G
    + F . G => -> F -> G
    + F*    => -> \eps -> F(loop) -> \eps

# DFA -> RE

1. preved hrany na regularny prechodovy graf
    + spojim viac hran medzi dvoma hranami do jednej

2. preved na specificky RE
    + 1 vstupny vrchol
    + 1 vystupny vrchol
    + jednu prechodovu funckiu E

3. odpoveda regularnemu vyrazu E

# Normalizacia RE

1. odstranenie nedosazitenlych stavov
2. odstranenie stavov kde vedie sipka len sama do seba
3. premen
    + r (->F) g (->G) q         => r (->F.G) q
    + r (->F) g (->E) g (->G) q => r (->F.E*.G) q

# regularne gramatiky na FA

1. premen vsetky pravidla S -> aT na S (->a) T
2. premen vsetky pravidla U -> a  na U (->a) ((qf))

# NFA to regularne gramatiky

1. δ(q, a)          => Q -> aP
2. δ(q, a); q in P  => Q - a
3. δ(q0, a)         => S -> aP
4. δ(q0, a)         => S -> aP
5. q0 in F          ....


