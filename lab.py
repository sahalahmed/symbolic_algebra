"""
6.1010 Spring '23 Lab 10: Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    precedence = float("inf")
    right_parens = False
    left_parens = False

    def simplify(self):
        return self


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        try:
            return mapping[self.name]
        except:
            raise NameError

    def __eq__(self, other):
        if isinstance(self, Var) and isinstance(other, Var):
            return self.name == other.name
        else:
            return False

    def deriv(self, var):
        if var == self.name:
            return Num(1)
        else:
            return Num(0)


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        return self.n

    def __eq__(self, other):
        if isinstance(self, Num) and isinstance(other, Num):
            return self.n == other.n
        else:
            return False

    def deriv(self, var):
        return Num(0)


class BinOp(Symbol):
    def __init__(self, left, right):
        """
        Initializer. Store instance variables called `left` and `right`,
        representing the left-hand and right-hand operand respectively.
        """
        if isinstance(left, (int, float)):
            left = Num(left)
        elif isinstance(left, str):
            left = Var(left)

        if isinstance(right, (int, float)):
            right = Num(right)
        elif isinstance(right, str):
            right = Var(right)

        self.left = left
        self.right = right

    def eval(self, mapping):
        l_val = self.left.eval(mapping)
        r_val = self.right.eval(mapping)

        return self.compute(l_val, r_val)

    def __str__(self):
        l_str = str(self.left)
        r_str = str(self.right)
        if self.left.precedence < self.precedence and not self.left_parens:
            l_str = f"({l_str})"
        if self.right.precedence < self.precedence:
            r_str = f"({r_str})"
        if self.right_parens and self.right.precedence == self.precedence:
            r_str = f"({r_str})"
        if self.left_parens and self.left.precedence <= self.precedence:
            l_str = f"({l_str})"
        return f"{l_str} {self.operation} {r_str}"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def __eq__(self, other):
        if isinstance(self, BinOp) and isinstance(other, BinOp):
            return (
                self.operation == other.operation
                and self.left == other.left
                and self.right == other.right
            )
        else:
            return False


class Add(BinOp):
    operation = "+"
    precedence = 2

    def compute(self, left, right):
        return left + right

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)

    def simplify(self):
        l_simplified = self.left.simplify()
        r_simplified = self.right.simplify()
        if isinstance(l_simplified, Num):
            if isinstance(r_simplified, Num):
                return Num(l_simplified.n + r_simplified.n)
            if l_simplified.n == 0:
                return r_simplified
        if isinstance(r_simplified, Num) and r_simplified.n == 0:
            return l_simplified
        return Add(l_simplified, r_simplified)


class Sub(BinOp):
    operation = "-"
    precedence = 2
    right_parens = True

    def compute(self, left, right):
        return left - right

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        l_simplified = self.left.simplify()
        r_simplified = self.right.simplify()
        if isinstance(l_simplified, Num) and isinstance(r_simplified, Num):
            return Num(l_simplified.n - r_simplified.n)
        if isinstance(r_simplified, Num) and r_simplified.n == 0:
            return l_simplified
        return Sub(l_simplified, r_simplified)


class Mul(BinOp):
    operation = "*"
    precedence = 3

    def compute(self, left, right):
        return left * right

    def deriv(self, var):
        return self.left * self.right.deriv(var) + self.right * self.left.deriv(var)

    def simplify(self):
        l_simplified = self.left.simplify()
        r_simplified = self.right.simplify()
        if isinstance(l_simplified, Num):
            if isinstance(r_simplified, Num):
                return Num(l_simplified.n * r_simplified.n)
            if l_simplified.n == 1:
                return r_simplified
            if l_simplified.n == 0:
                return Num(0)
        if isinstance(r_simplified, Num):
            if r_simplified.n == 1:
                return l_simplified
            if r_simplified.n == 0:
                return Num(0)
        return Mul(l_simplified, r_simplified)


class Div(BinOp):
    operation = "/"
    precedence = 3
    right_parens = True

    def compute(self, left, right):
        return left / right

    def deriv(self, var):
        return (
            self.right * self.left.deriv(var) - self.left * self.right.deriv(var)
        ) / (self.right * self.right)

    def simplify(self):
        l_simplified = self.left.simplify()
        r_simplified = self.right.simplify()
        if isinstance(l_simplified, Num):
            if isinstance(r_simplified, Num):
                return Num(l_simplified.n / r_simplified.n)
            if l_simplified.n == 0:
                return Num(0)
        if isinstance(r_simplified, Num) and r_simplified.n == 1:
            return l_simplified
        return Div(l_simplified, r_simplified)


class Pow(BinOp):
    operation = "**"
    precedence = 4
    left_parens = True

    def compute(self, left, right):
        return left**right

    def deriv(self, var):
        if not isinstance(self.right, Num):
            raise TypeError("Can only take derivative of Pow with a Num exponent")
        return self.right * self.left ** (self.right - Num(1)) * self.left.deriv(var)

    def simplify(self):
        l_simplified = self.left.simplify()
        r_simplified = self.right.simplify()
        if isinstance(l_simplified, Num):
            if isinstance(r_simplified, Num):
                return Num(l_simplified.n**r_simplified.n)
            if l_simplified.n == 0:
                if isinstance(r_simplified, Num) and r_simplified.n < 0:
                    return Pow(l_simplified, r_simplified)
                return Num(0)
        if isinstance(r_simplified, Num):
            if r_simplified.n == 0:
                return Num(1)
            if r_simplified.n == 1:
                return l_simplified
        return Pow(l_simplified, r_simplified)


def expression(string):
    tokens = tokenize(string)
    return parse(tokens)


digits = "0123456789"
alphanumeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def tokenize(string):
    tokens = []
    i = 0
    while i < len(string):
        if string[i] in digits or string[i] == "-":
            start = i
            i += 1
            while i < len(string) and (string[i] in digits or string[i] == "."):
                i += 1
            tokens.append(string[start:i])
        elif string[i] == " ":
            i += 1
        elif string[i] == "*":
            if string[i + 1] == "*":
                tokens.append("**")
                i += 2
            else:
                tokens.append(string[i])
                i += 1
        else:
            tokens.append(string[i])
            i += 1
    return tokens


def parse(tokens):
    def parse_expression(index):
        token = tokens[index]

        if token[0] in digits or token[0] == "-":
            return Num(float(token)), index + 1

        if token in alphanumeric:
            return Var(token), index + 1

        if token == "(":
            l_expression, next_index = parse_expression(index + 1)
            operation = tokens[next_index]
            r_expression, next_index = parse_expression(next_index + 1)

            if operation == "+":
                return Add(l_expression, r_expression), next_index + 1
            if operation == "-":
                return Sub(l_expression, r_expression), next_index + 1
            if operation == "*":
                return Mul(l_expression, r_expression), next_index + 1
            if operation == "/":
                return Div(l_expression, r_expression), next_index + 1
            if operation == "**":
                return Pow(l_expression, r_expression), next_index + 1

    parsed_expression, next_index = parse_expression(0)
    return parsed_expression


if __name__ == "__main__":
    doctest.testmod()
