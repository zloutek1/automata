import sys
import types

from utils import Set


class PDA:
    def __init__(self, Q, Σ, Γ, δ, q0, Z0, F):
        """

        Q  : set of states
        Σ  : finite alphabet
        Γ  : set of alphabet of Stack
        δ  : Q × Σ → Q transition function
        q0 : q0 ∈ Q initial states
        Z0 : initial symbol in Stack
        F  : F ⊆ Q set of accepting states

        """
        import PDA

        assert isinstance(Q, Set), "Q must be a Set of states"
        assert isinstance(Σ, Set), "Σ must be a Set of alphabet"
        if not (isinstance(δ, PDA.δ) or isinstance(δ, PDA.ô)):
            raise AssertionError(
                f"δ must be a transition function PDA.δ, but is {type(δ)}")
        assert q0 in Q, f"condition q0 ∈ Q not met, {q0} not in {Q}"
        assert isinstance(F, Set), "F must be a Set of accepting states"
        assert all(qf in Q for qf in F) or F.empty(
        ), f"condition F ⊆ Q not met, element of {F} not in {Q}"

        self.__dict__.update({
            "Q": Q.map(str), "Σ": Σ.map(str), "Γ": Γ.map(str), "δ": δ, "q0": str(q0), "Z0": str(Z0), "F": F.map(str)})

        self.δ.pda = self

    def __str__(self):
        return (f"A = ({self.Q}, {self.Σ}, {self.Γ}, δ, {self.q0}, {self.Z0}, {self.F}) where\n" +
                f"δ = {self.δ if getattr(self, 'δ', False) else self.ô}\n")


class δ(dict):
    def __setitem__(self, key, val):
        super().__setitem__(tuple(map(str, key)), Set(map(str, val)))

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, Set())
        return super().__getitem__(key)


class ô(dict):
    def __setitem__(self, key, val):
        super().__setitem__(key, val)

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, Set())
        return super().__getitem__(key)


class call(types.ModuleType):
    """
    make the module callable simplifying
    from PDA import PDA
    to
    import PDA
    """

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self, *args, **kwargs):
        return PDA(*args, **kwargs)


sys.modules[__name__] = call()
