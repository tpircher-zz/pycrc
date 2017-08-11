#  pycrc -- parameterisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2017  Thomas Pircher  <tehpeh-web@tty1.net>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.


"""
This modules simplifies an expression.

    import pycrc.expr as exp

    my_expr = exp.Xor('var', exp.Parenthesis(exp.And('0x700', 4)))
    print('"{}" -> "{}"'.format(my_expr, my_expr.simplify()))
"""


def _classify(val):
    """
    Creates a Terminal object if the parameter is a string or an integer.
    """
    if type(val) is int:
        return Terminal(val)
    if type(val) is str:
        if val.isdigit():
            return Terminal(int(val), val)
        if val[:2].lower() == '0x':
            return Terminal(int(val, 16), val)
        return Terminal(val)
    return val


class Expression(object):
    """
    Base class for all expressions.
    """
    def is_int(self, val = None):
        return False


class Terminal(Expression):
    """
    A terminal object.
    """
    def __init__(self, val, pretty = None):
        """
        Construct a Terminal.
        The val variable is usually a string or an integer. Integers may also
        be passed as strings. The pretty-printer will use the string when
        formatting the expression.
        """
        self.val = val
        self.pretty = pretty

    def __str__(self):
        """
        Return the string expression of this object.
        """
        if self.pretty is None:
            return str(self.val)
        return self.pretty

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        return self

    def is_int(self, val = None):
        """
        Return True if the value of this Terminal is an integer.
        """
        if type(self.val) is int:
            return val is None or self.val == val
        return False


class FunctionCall(Expression):
    """
    Represent a function call
    """
    def __init__(self, name, args):
        """
        Construct a function call object.
        """
        self.name = _classify(name)
        self.args = [_classify(arg) for arg in args]

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.name) + '(' + ', '.join([str(arg) for arg in self.args]) + ')'

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        args = [arg.simplify() for arg in self.args]
        return FunctionCall(self.name, args)


class Parenthesis(Expression):
    """
    Represent a pair of round brackets.
    """
    def __init__(self, val):
        """
        Construct a parenthesis object.
        """
        self.val = _classify(val)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        val = self.val.simplify()
        if type(val) is Terminal:
            return val
        return Parenthesis(val)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return '(' + str(self.val) + ')'


class Add(Expression):
    """
    Represent an addition of operands.
    """
    def __init__(self, lhs, rhs):
        """
        Construct an addition object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val + rhs.val)
        if lhs.is_int(0):
            return rhs
        if rhs.is_int(0):
            return lhs
        return Add(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' + ' + str(self.rhs)


class Sub(Expression):
    """
    Represent a subtraction of operands.
    """
    def __init__(self, lhs, rhs):
        """
        Construct subtraction object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val - rhs.val)
        if lhs.is_int(0):
            return rhs
        if rhs.is_int(0):
            return lhs
        return Sub(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' - ' + str(self.rhs)


class Mul(Expression):
    """
    Represent the multiplication of operands.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a multiplication object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val * rhs.val)
        if lhs.is_int(0) or rhs.is_int(0):
            return Terminal(0)
        if lhs.is_int(1):
            return rhs
        if rhs.is_int(1):
            return lhs
        return Mul(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' * ' + str(self.rhs)


class Shl(Expression):
    """
    Shift left operation.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a shift left object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val << rhs.val)
        if lhs.is_int(0):
            return Terminal(0)
        if rhs.is_int(0):
            return lhs
        return Shl(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' << ' + str(self.rhs)


class Shr(Expression):
    """
    Shift right operation.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a shift right object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val >> rhs.val)
        if lhs.is_int(0):
            return Terminal(0)
        if rhs.is_int(0):
            return lhs
        return Shr(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' >> ' + str(self.rhs)


class Or(Expression):
    """
    Logical or operation.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a logical and object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val | rhs.val)
        if lhs.is_int(0):
            return rhs
        if rhs.is_int(0):
            return lhs
        return Or(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' | ' + str(self.rhs)


class And(Expression):
    """
    Logical and operation.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a logical and object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val & rhs.val)
        if lhs.is_int(0) or rhs.is_int(0):
            return Terminal(0)
        return And(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' & ' + str(self.rhs)


class Xor(Expression):
    """
    Logical xor operation.
    """
    def __init__(self, lhs, rhs):
        """
        Construct a logical xor object.
        """
        self.lhs = _classify(lhs)
        self.rhs = _classify(rhs)

    def simplify(self):
        """
        Return a simplified version of this sub-expression.
        """
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        if lhs.is_int() and rhs.is_int():
            return Terminal(lhs.val ^ rhs.val)
        if lhs.is_int(0):
            return rhs
        if rhs.is_int(0):
            return lhs
        return Xor(lhs, rhs)

    def __str__(self):
        """
        Return the string expression of this object.
        """
        return str(self.lhs) + ' ^ ' + str(self.rhs)
