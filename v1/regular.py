
class RE:
    pass


class RETransitionFunction(dict):
    def __init__(self, Σ, *args, **kwargs):
        self.alphabet = sorted(Σ)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 2:
            # δ[1, "a"] = 1; δ[1, "a"] = 2
            if value is not None:
                super().__setitem__(key, value)
            return
