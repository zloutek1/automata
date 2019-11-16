from collections.abc import Iterable


def roman(num):
    """

    Convert an integer to a Roman numeral.

    """

    if not 0 < num < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC',
            'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []
    for i in range(len(ints)):
        count = int(num / ints[i])
        result.append(nums[i] * count)
        num -= ints[i] * count
    return ''.join(result)


class Set:
    """

    Ordered set

    """

    def __init__(self, *args):

        if len(args) == 1 and isinstance(args[0], Iterable) and type(args[0]) not in (Set, str):
            seen = set()
            self.values = [arg for arg in args[0]
                           if not (arg in seen or seen.add(arg))]

        else:
            seen = set()
            self.values = [arg for arg in args
                           if not (arg in seen or seen.add(arg))]

    @classmethod
    def Union(set, sets):
        result = Set()
        for s in sets:
            result = result.union(s)
        return result

    def union(self, other):
        seen = set()
        return Set([x for x in self.values + other.values if not (x in seen or seen.add(x))])

    def __or__(self, other):
        return self.union(other)

    def add(self, other):
        self.values = self.union(Set(other)).values

    def __add__(self, other):
        return self.union(other)

    def intercept(self, other):
        return Set([x for x in self.values + other.values if x in other.values and x in self.values])

    def cross(self, other):
        return Set((p, q) for p in self for q in other)

    def difference(self, other):
        return Set([x for x in self.values if x not in other.values])

    def __sub__(self, other):
        return self.difference(other)

    def __len__(self):
        return len(self.values)

    def empty(self):
        return len(self.values) == 0

    def __iter__(self):
        return iter(self.values)

    def __eq__(self, other):
        return set(self) == set(other)

    def __hash__(self):
        return sum(map(hash, self.values))

    def pop(self, index=-1):
        return self.values.pop(index)

    def __getitem__(self, key):
        return self.values[key]

    def __repr__(self):
        return f"{{{', '.join(map(str, self.values))}}}" if len(self.values) != 0 else 'Ø'


"""

RegexParser https://xysun.github.io/posts/regex-parsing-thompsons-algorithm.html

"""


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        if self.name == "CHAR":
            return self.value
        return self.name


class Lexer:
    def __init__(self, pattern):
        self.source = pattern
        self.symbols = {'(': 'LEFT_PAREN',
                        ')': 'RIGHT_PAREN',
                        '*': 'STAR',
                        '+': 'ALT',
                        '.': 'CONCAT', }
        self.current = 0
        self.length = len(self.source)

    def get_token(self):
        if self.current < self.length:
            c = self.source[self.current]
            self.current += 1
            if c not in self.symbols.keys():  # CHAR
                token = Token('CHAR', c)
            else:
                token = Token(self.symbols[c], c)
            return token
        else:
            return Token('NONE', '')


class ParseError(Exception):
    pass


'''
Grammar for regex:
regex = exp $
exp      = term [+] exp      {push '+'}
         | term
         |                   empty?
term     = factor term       chain {add \x08}
         | factor
factor   = primary [*]       star {push '*'}
         | primary
primary  = \( exp \)
         | char              literal {push char}
'''


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []
        self.lookahead = self.lexer.get_token()

    def consume(self, name):
        if self.lookahead.name == name:
            self.lookahead = self.lexer.get_token()
        elif self.lookahead.name != name:
            raise ParseError(f"Error on token {self.lookahead}")

    def parse(self):
        self.exp()
        return self.tokens

    def exp(self):
        self.term()
        if self.lookahead.name == 'ALT':
            t = self.lookahead
            self.consume('ALT')
            self.exp()
            self.tokens.append(t)

    def term(self):
        self.factor()
        if self.lookahead.value not in ')+':
            self.consume("CONCAT")
            self.term()
            self.tokens.append(Token("CONCAT", "."))

    def factor(self):
        self.primary()
        if self.lookahead.name in ['STAR']:
            self.tokens.append(self.lookahead)
            self.consume(self.lookahead.name)

    def primary(self):
        if self.lookahead.name == 'LEFT_PAREN':
            self.consume('LEFT_PAREN')
            self.exp()
            self.consume('RIGHT_PAREN')
        elif self.lookahead.name == 'CHAR':
            self.tokens.append(self.lookahead)
            self.consume('CHAR')


def parseRegex(regexp):
    lexer = Lexer(regexp)
    return Parser(lexer).parse()


"""

RegexParser https://xysun.github.io/posts/regex-parsing-thompsons-algorithm.html

"""