# IB102 Finite automata and grammar

    **Note that this is a fun personal project, nowhere near fully functional**

    ## supported types:
        ### regular
        + DFA : Deterministic Finite Automata
        + NFA : Non-deterministic Finite Automata
        + EFA : NFA with ε steps
        + RE : Regular Expression Valued Automata
        + G : Regular Grammar

        ## context-free
        + PDA : Pushdown Automata
        + CFG : Context free Grammar
        + TopDown analyzer
        + BottomUp analyzer


    ## visual representation of Automata
        ### table
        ```
        +------------------------------------------+
        |      DETERMINISTIC FINITE AUTOMATA       |
        +------------------------------------------+

        Q  = {1, 2, 3, 4, 5, 6, 7}
        Σ  = {a, b}

        +---+-----+-----+
        |   |  a  |  b  |
        +---+-----+-----+
        | 1 |  2  |  -  |
        | 2 |  3  |  4  |
        | 3 |  6  |  5  |
        | 4 |  3  |  2  |
        | 5 |  6  |  3  |
        | 6 |  2  |  -  |
        | 7 |  6  |  1  |
        +---+-----+-----+

        I = {1}
        F  = {3, 5, 6}
        ```
        ### graph
        ![graph](https://graphviz.gitlab.io/_pages/Gallery/directed/fsm.png)
