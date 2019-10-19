from itertools import *
import functools
import operator


class GenCacher:
    def __init__(self, generator):
        self._g = iter(generator)
        self._cache = []

    def __getitem__(self, idx):
        while len(self._cache) <= idx:
            self._cache.append(next(self._g))
        return self._cache[idx]


"""
class Iterace:
    def __init__(self, jazyk, _from=0):
        self._args = None
        self.start_from = _from

        if isinstance(jazyk, Jazyk):
            self.jazyk = jazyk
            self._iter_args = self.args
            return

        if isinstance(jazyk, Iterace):
            self.jazyk = jazyk
            self._iter_args = self.args
            return

        self._args = jazyk

    @property
    def args(self):
        if self._args:
            return self._args
        return map(lambda arg: Slovo("".join(map(repr, arg))), chain.from_iterable(product(self.jazyk, repeat=i) for i in count(self.start_from)))

    def __iter__(self):
        return iter(self.args)

    def __mul__(self, _other):
        if isinstance(_other, Iterace):
            return Iterace(self.product(self, _other))

        if isinstance(_other, Jazyk):
            return Iterace(chain.from_iterable(map(lambda slovo: [
                slovo * _other_slovo for _other_slovo in _other], self)))

        raise NotImplementedError()

    def __pow__(self, to):
        if isinstance(to, int):
            if to <= 0:
                return Jazyk(Slovo(""))
            return self * self ** (to - 1)

        if to == "*":
            return Iterace(self.args)

        raise NotImplementedError()

    def __repr__(self):
        slova = str(sorted(islice(self.args, 10), key=abs))
        return f"{{{slova[1:-1]}, ...}}"

    @staticmethod
    def product(gen1, gen2):
        gc1 = GenCacher(gen1)
        gc2 = GenCacher(gen2)
        idx1 = idx2 = 0
        moving_up = True

        while True:
            yield (gc1[idx1] * gc2[idx2])

            if moving_up and idx1 == 0:
                idx2 += 1
                moving_up = False
            elif not moving_up and idx2 == 0:
                idx1 += 1
                moving_up = True
            elif moving_up:
                idx1, idx2 = idx1 - 1, idx2 + 1
            else:
                idx1, idx2 = idx1 + 1, idx2 - 1
"""


class Iterace:
    def __init__(self, val, from_power=0):
        self.from_power = from_power
        self._args = None

        if isinstance(val, Jazyk):
            self.val = val
            return

        self._args = val

    @property
    def args(self):
        if self._args:
            return self._args
        return self._get_args()

    def _get_args(self):
        return chain.from_iterable(
            sorted(
                map(lambda arg:
                    Slovo(
                        "".join(map(repr, arg))
                    ),
                    product(self.val, repeat=i)
                    ),
                key=lambda slovo: (abs(slovo), slovo)
            )
            for i in count(self.from_power)
        )

    def __mul__(self, _other):
        if isinstance(_other, Jazyk):
            return Iterace(chain.from_iterable(map(lambda slovo: [
                slovo * _other_slovo for _other_slovo in _other], self)))

    def __pow__(self, to):
        if isinstance(to, int):
            if to <= 0:
                return Jazyk(Slovo(""))
            return self * self ** (to - 1)

        if to == "*":
            return Iterace(self)

    def __iter__(self):
        return iter(self.args)

    def __repr__(self):
        slova = str(list(islice(self.args, 10)))
        return f"{{{slova[1:-1]}, ...}}"


class Slovo:
    def __init__(self, val, *, Σ=None):
        if not Σ:
            self.Σ = globals().get("Σ")
        else:
            self.Σ = Σ

        if isinstance(val, str):
            self.val = val
            assert self.check_buildable(
                self.val, self.Σ), f"Slovo {self.val} nepatri do abecedy Σ"
            return

        if isinstance(val, Slovo):
            self.val = val.val
            assert self.check_buildable(
                self.val, self.Σ), f"Slovo {self.val} nepatri do abecedy Σ"
            return

        raise TypeError("unsuported type for val in slovo")

    def check_buildable(self, slovo, from_Σ):
        buildable = False
        if from_Σ:
            for hlaska in from_Σ:
                if hlaska == slovo[:abs(hlaska)]:
                    buildable = True
                    buildable &= self.check_buildable(
                        slovo[abs(hlaska):], from_Σ)
        if not from_Σ or len(slovo) == 0:
            return True
        return buildable

    def 井(self, _of):
        if isinstance(_of, str):
            return self.val.count(_of)

    def __pow__(self, to):
        if to == "R":
            return Slovo(self.val[::-1])

        elif isinstance(to, int):
            return Slovo(self.val * to)

    def __mul__(self, _with):
        if isinstance(_with, Slovo):
            return Slovo(self.val + _with.val)

    def __eq__(self, _with):
        if isinstance(_with, Slovo):
            return repr(self) == repr(_with)

        if isinstance(_with, str):
            if self.val == "" and _with == "Ɛ":
                return True
            return self.val == _with

    def __lt__(self, _with):
        if isinstance(_with, Slovo):
            return self.val < _with.val

    def __abs__(self):
        return len(self.val)

    def __hash__(self):
        return hash(self.val)

    def __repr__(self):
        if len(self.val) == 0:
            return "Ɛ"
        return str(self.val)


def 井(_of, _in):
    return _in.井(_of)


R = "R"


class Jazyk:
    def __init__(self, *args):
        args = list(args)

        if isinstance(args[0], tuple):
            self.args = set(args[0])
            return

        if isinstance(args[0], set):
            self.args = args[0]
            return

        if isinstance(args[0], Jazyk):
            self.args = args[0].args
            return

        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = Slovo(arg)

        self.args = set(args)

    def __and__(self, _other):
        if isinstance(_other, Jazyk):
            return Jazyk(set(self.args) & set(_other.args))

    def __or__(self, _other):
        if isinstance(_other, Jazyk):
            return Jazyk(set(self.args) | set(_other.args))

    def __sub__(self, _other):
        if isinstance(_other, Jazyk):
            return Jazyk(set(self.args) - set(_other.args))

    def __mul__(self, _other):
        if isinstance(_other, Jazyk):
            return Jazyk(set(u * v for u in self.args for v in _other.args))

        elif isinstance(_other, Iterace):
            return _other * self

    def __pow__(self, to):
        if isinstance(to, int):
            if to <= 0:
                return Jazyk(Slovo(""))
            return Jazyk(self * self ** (to - 1))

        elif to == "*":
            return Iterace(self)

        elif to == "+":
            return Iterace(self, 1)

    def __eq__(self, _other):
        if isinstance(_other, Jazyk):
            return repr(self) == repr(_other)

        if isinstance(_other, set):
            return self.args == _other

    def __getitem__(self, key):
        return sorted(self.args)[key]

    def __abs__(self):
        return len(self.args)

    def __iter__(self):
        return iter(sorted(self.args))

    def __repr__(self):
        return f"{{{str(sorted(self.args))[1:-1]}}}"


class Abeceda:
    def __init__(self, *args):
        args = list(args)

        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = Slovo(arg)

        self.args = args

    def __pow__(self, to):
        return Jazyk(*self.args) ** to

    def __iter__(self):
        return iter(list(self.args))

    def __repr__(self):
        return f"{{{str(sorted(self.args))[1:-1]}}}"

#
#
# Code here


"""
u = Slovo("abba")
v = Slovo("ca")

assert u * v == "abbaca"
assert abs(u) == 4
assert 井("b", u) == 2
assert u ** 2 == "abbaabba"
assert u ** 3 == "abbaabbaabba"
assert u ** 0 == ""
assert u ** 0 == "Ɛ"
assert v ** R == "ac"

L1 = Jazyk(Slovo("xy"), Slovo("y"), Slovo("yx"))
L2 = Jazyk(Slovo("y"), Slovo("z"))

assert L1 & L2 == {"y"}
assert L1 | L2 == {"xy", "y", "yx", "z"}
assert L1 - L2 == {"xy", "yx"}
assert L1 * L2 == {"xyy", "yy", "yxy", "xyz", "yz", "yxz"}

assert L1 ** 0 == {""}
assert L1 ** 1 == L1
assert L1 ** 2 == {"yxxy", "yxy", "xyxy", "xyyx", "yyx", "yy", "xyy", "yxyx"}

L1 = Jazyk("a")**"*"
L2 = Jazyk("b")**"*"
print(L1 * L2)

Σ = Abeceda("ab", "bc")
print((Σ ** "*"))
"""

print((Slovo("bab")**R * Slovo("ba")**R)**2)

L1 = Jazyk("ba", "ab", "")
L2 = Jazyk("b")
L3 = Jazyk("a", "")

a = L1 * L2
b = a ** "*"
c = b * L3
print(type(a), a)
print(type(b), b)
print(type(c), c)
print(c ** 1)
