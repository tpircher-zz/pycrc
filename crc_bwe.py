#  pycrc -- parametrisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2012-2012  Thomas Pircher  <tehpeh@gmx.net>
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
Simplification of a bitwise C expression.
"""

from __future__ import print_function
import sys
import re
import itertools
import functools


# Class _ExpNode
###############################################################################
class _ExpNode:
    """
    The node of a parse tree.
    """
    ID_UNDEF        = 0
    ID_INTEGER      = 1
    ID_IDENTIFIER   = 2
    ID_BITWISE_NEG  = 3
    ID_BITWISE_AND  = 4
    ID_BITWISE_OR   = 5
    ID_BITWISE_XOR  = 6
    ID_LSHIFT       = 7
    ID_RSHIFT       = 8

    ALL_ZEROS       = 0
    ALL_ONES        = ~0


    # function __init__
    ###############################################################################
    def __init__(self, node_type = ID_UNDEF, values = None, or_mask = ALL_ZEROS, and_mask = ALL_ONES):
        """
        The class constructor.
        """
        self.node_type = node_type
        self.or_mask = or_mask & and_mask
        self.and_mask = and_mask
        if self.node_type == _ExpNode.ID_INTEGER:
            self.values = (values | or_mask) & and_mask
        else:
            self.values = values
        self.sanity_check()


    # function sanity_check
    ###############################################################################
    def sanity_check(self):
        """
        Check the class for consistency.
        """
        if not __debug__:
            return
        if self.node_type == self.ID_INTEGER:
            assert type(self.values) == int or type(self.values) == long
            assert (self.values | self.or_mask) & self.and_mask == self.values
        elif self.node_type == self.ID_IDENTIFIER:
            assert type(self.values) == str
        elif self.node_type == self.ID_BITWISE_NEG:
            assert isinstance(self.values, _ExpNode)
        elif self.node_type == self.ID_BITWISE_AND:
            assert type(self.values) == list
            assert len(self.values) > 1
        elif self.node_type == self.ID_BITWISE_OR:
            assert type(self.values) == list
            assert len(self.values) > 1
        elif self.node_type == self.ID_BITWISE_XOR:
            assert type(self.values) == list
            assert len(self.values) > 1
        elif self.node_type == self.ID_LSHIFT:
            assert type(self.values) == list
            assert len(self.values) == 2
        elif self.node_type == self.ID_RSHIFT:
            assert type(self.values) == list
            assert len(self.values) == 2
        else:
            raise ValueError()
        assert self.or_mask & self.and_mask == self.or_mask
        assert self.or_mask | self.and_mask == self.and_mask


    # function to_string
    ###############################################################################
    def to_string(self, use_paren = False):
        """
        Pretty-print a parse tree.

        Parameters:
            use_paren: use patnthesis on a non-trivial node.

        Return:
            The node (and its sub-nodes) as a C expression.
        """
        self.sanity_check()

        if self.node_type == _ExpNode.ID_INTEGER:
            return "%uu" % self.values
        elif self.node_type == _ExpNode.ID_IDENTIFIER:
            return self.values
        elif self.node_type == _ExpNode.ID_BITWISE_NEG:
            return "~" + self.values.to_string(True)
        elif self.node_type == _ExpNode.ID_BITWISE_AND:
            res = " & ".join([value.to_string(True) for value in self.values])
            return "(" + res + ")" if use_paren else res
        elif self.node_type == _ExpNode.ID_BITWISE_OR:
            res = " | ".join([value.to_string(True) for value in self.values])
            return "(" + res + ")" if use_paren else res
        elif self.node_type == _ExpNode.ID_BITWISE_XOR:
            res = " ^ ".join([value.to_string(True) for value in self.values])
            return "(" + res + ")" if use_paren else res
        elif self.node_type == _ExpNode.ID_LSHIFT:
            res = " << ".join([value.to_string(True) for value in self.values])
            return "(" + res + ")" if use_paren else res
        elif self.node_type == _ExpNode.ID_RSHIFT:
            res = " >> ".join([value.to_string(True) for value in self.values])
            return "(" + res + ")" if use_paren else res
        else:
            raise ValueError()



# Class _ExpParseError
###############################################################################
class _ExpParseError(Exception):
    """
    The exception class for the parser.
    """

    # Class constructor
    ###############################################################################
    def __init__(self, reason):
        self.reason = reason

    # function __str__
    ###############################################################################
    def __str__(self):
        return self.reason


# Class _ExpLexer
###############################################################################
class _ExpLexer:
    """
    The (private) lexer class.
    """
    TOK_UNKNOWN     = 0
    TOK_EOF         = 1
    TOK_RSHIFT      = 2
    TOK_LSHIFT      = 3
    TOK_LOGIC_NOT   = 4
    TOK_LOGIC_OR    = 5
    TOK_LOGIC_XOR   = 6
    TOK_LOGIC_AND   = 7
    TOK_LPAREN      = 8
    TOK_RPAREN      = 9
    TOK_INTEGER     = 10
    TOK_IDENTIFIER  = 11

    # Regular Expressions used by the parser.
    re_id = re.compile("^[a-zA-Z][a-zA-Z0-9_-]*")
    re_num = re.compile("^(0[xX][0-9a-fA-F]+|[0-9]+)")
    re_op = re.compile("^([|&^~()]|>>|<<)")


    # function __init__
    ###############################################################################
    def __init__(self, expr = ""):
        """
        The class constructor.
        """
        self._in_str = expr
        self._in_str_pos = 0
        self._in_str_peek = 0
        self._next_token = None
        self.text = ""


    # function peek
    ###############################################################################
    def peek(self):
        """
        Return the next token, without taking it away from the input string.

        Return:
            The next token.
        """
        # Token already found?
        if self._next_token != None:
            return self._next_token

        # Remove white space
        while self._in_str_pos < len(self._in_str) and \
                self._in_str[self._in_str_pos].isspace():
            self._in_str_pos += 1

        # End-of-file?
        if self._in_str_pos >= len(self._in_str):
            self._in_str_peek = self._in_str_pos
            self.text = ""
            self._next_token = self.TOK_EOF
            return self.TOK_EOF

        # Match on operator
        m = self.re_op.match(self._in_str[self._in_str_pos:])
        if m != None:
            self._in_str_peek = self._in_str_pos + m.end()
            self.text = m.group(0)
            if self.text == '(':
                self._next_token = self.TOK_LPAREN
            elif self.text == ')':
                self._next_token = self.TOK_RPAREN
            elif self.text == '~':
                self._next_token = self.TOK_LOGIC_NOT
            elif self.text == '|':
                self._next_token = self.TOK_LOGIC_OR
            elif self.text == '^':
                self._next_token = self.TOK_LOGIC_XOR
            elif self.text == '&':
                self._next_token = self.TOK_LOGIC_AND
            elif self.text == '>>':
                self._next_token = self.TOK_RSHIFT
            elif self.text == '<<':
                self._next_token = self.TOK_LSHIFT
            else:
                self._next_token = self.TOK_UNKNOWN
                assert False
            return self._next_token

        m = self.re_id.match(self._in_str[self._in_str_pos:])
        if m != None:
            self._in_str_peek = self._in_str_pos + m.end()
            self.text = m.group(0)
            self._next_token = self.TOK_IDENTIFIER
            return self._next_token

        m = self.re_num.match(self._in_str[self._in_str_pos:])
        if m != None:
            self._in_str_peek = self._in_str_pos + m.end()
            self.text = m.group(1)
            self._next_token = self.TOK_INTEGER
            return self._next_token
        
        self._in_str_peek = self._in_str_pos + 1
        self.text = self._in_str[self._in_str_pos:self._in_str_peek]
        self._next_token = self.TOK_UNKNOWN
        return self._next_token


    # function advance
    ###############################################################################
    def advance(self):
        """
        Discard the current symbol from the input stream and advance to the
        following characters.
        """
        self._in_str_pos = self._in_str_peek
        self._next_token = None
        self.text = ""



# Class BitwiseExpression
###############################################################################
class BitwiseExpression:
    """
    The Bitwise Expression class.
    """

    # function _print
    ###############################################################################
    def _print(self, ptree):
        """
        Pretty-print a parse tree.

        Parameters:
            ptree: the parse tree to pretty-print.

        Return:
            The parse tree as a C expression.
        """
        ptree.sanity_check()
        return ptree.to_string()


    # function _parse
    #
    # The used grammar is:
    #   stmt:
    #               | expr_or
    #               ;
    #
    #   expr_or:      expr_xor
    #               | expr_or '|' expr_xor
    #               ;
    #
    #   expr_xor:     expr_and
    #               | expr_xor '^' expr_and
    #               ;
    #
    #   expr_and:     expr_shift
    #               | expr_and '&' expr_shift
    #               ;
    #
    #   expr_shift:   terminal
    #               | terminal OP_LSHIFT terminal
    #               | terminal OP_RSHIFT terminal
    #               ;
    #
    #   terminal:     INTEGER
    #               | IDENTIFIER
    #               | '~' terminal
    #               | '(' expr_or ')'
    #               ;
    ###############################################################################
    def _parse(self, expr):
        """
        Parse a C expression.

        Parameters:
            expr: a string with the C expression to simplify.

        Return:
            Returns the parse tree for the expression.
        """
        self._lex = _ExpLexer(expr)
        tok = self._lex.peek()
        if tok == self._lex.TOK_EOF:
            return _ExpNode(_ExpNode.ID_INTEGER, 0)
        ptree = self._parse_or()
        if ptree == None:
            raise _ExpParseError("%s: error: error at token '%s'" % (sys.argv[0], self._lex.text))
            return None
        tok = self._lex.peek()
        if tok != self._lex.TOK_EOF:
            raise _ExpParseError("%s: error: unknown terminal '%s'" % (sys.argv[0], self._lex.text))
            return None
        return ptree


    # function _parse_or
    ###############################################################################
    def _parse_or(self):
        """
        Parse an OR expression.

        Return:
            Returns the parse tree of the (sub-)expression.
        """
        operands = []
        tok = self._lex.peek()
        while tok != self._lex.TOK_EOF:
            node = self._parse_xor()
            if node == None:
                # Hand the parse error down.
                return None

            operands.append(node)
            tok = self._lex.peek()
            # expect an 'or' token.
            if tok == self._lex.TOK_LOGIC_OR:
                self._lex.advance()
            # everything else marks the end of this sub-expression
            else:
                break
        if len(operands) == 1:
            return operands[0]
        elif len(operands) > 1:
            return _ExpNode(_ExpNode.ID_BITWISE_OR, operands)
        return None


    # function _parse_xor
    ###############################################################################
    def _parse_xor(self):
        """
        Parse an XOR expression.

        Return:
            Returns the parse tree of the (sub-)expression.
        """
        operands = []
        tok = self._lex.peek()
        while tok != self._lex.TOK_EOF:
            node = self._parse_and()
            if node == None:
                # Hand the parse error down.
                return None

            operands.append(node)
            tok = self._lex.peek()
            # expect an 'xor' token.
            if tok == self._lex.TOK_LOGIC_XOR:
                self._lex.advance()
            # everything else marks the end of this sub-expression
            else:
                break
        if len(operands) == 1:
            return operands[0]
        elif len(operands) > 1:
            return _ExpNode(_ExpNode.ID_BITWISE_XOR, operands)
        return None


    # function _parse_and
    ###############################################################################
    def _parse_and(self):
        """
        Parse an AND expression.

        Return:
            Returns the parse tree of the (sub-)expression.
        """
        operands = []
        tok = self._lex.peek()
        while tok != self._lex.TOK_EOF:
            node = self._parse_shift()
            if node == None:
                # Hand the parse error down.
                return None

            operands.append(node)
            tok = self._lex.peek()
            # expect an 'and' token.
            if tok == self._lex.TOK_LOGIC_AND:
                self._lex.advance()
            # everything else marks the end of this sub-expression
            else:
                break
        if len(operands) == 1:
            return operands[0]
        elif len(operands) > 1:
            return _ExpNode(_ExpNode.ID_BITWISE_AND, operands)
        return None


    # function _parse_shift
    ###############################################################################
    def _parse_shift(self):
        """
        Parse an SHIFT expression.

        Return:
            Returns the parse tree of the (sub-)expression.
        """
        node = self._parse_terminal()
        if node == None:
            # Hand the parse error down.
            return None

        tok = self._lex.peek()
        # expect an '<<' token.
        if tok == self._lex.TOK_LSHIFT:
            operands = [node]
            self._lex.advance()
            node = self._parse_terminal()
            if node == None:
                return None
            operands.append(node)
            return _ExpNode(_ExpNode.ID_LSHIFT, operands)
        elif tok == self._lex.TOK_RSHIFT:
            operands = [node]
            self._lex.advance()
            node = self._parse_terminal()
            if node == None:
                return None
            operands.append(node)
            return _ExpNode(_ExpNode.ID_RSHIFT, operands)
        return node


    # function _parse_terminal
    ###############################################################################
    def _parse_terminal(self):
        """
        Parse a terminal.

        Return:
            Returns the parse tree of the (sub-)expression.
        """
        tok = self._lex.peek()
        if tok == self._lex.TOK_IDENTIFIER:
            node = _ExpNode(_ExpNode.ID_IDENTIFIER, self._lex.text)
            self._lex.advance()
            return node
        elif tok == self._lex.TOK_INTEGER:
            if len(self._lex.text) > 1 and self._lex.text[1].upper() == 'X':
                node = _ExpNode(_ExpNode.ID_INTEGER, int(self._lex.text, 16))
            elif len(self._lex.text) > 1 and self._lex.text[1].upper() == 'B':
                node = _ExpNode(_ExpNode.ID_INTEGER, int(self._lex.text, 2))
            elif self._lex.text[0] == '0':
                node = _ExpNode(_ExpNode.ID_INTEGER, int(self._lex.text, 8))
            else:
                node = _ExpNode(_ExpNode.ID_INTEGER, int(self._lex.text))
            self._lex.advance()
            return node
        elif tok == self._lex.TOK_LOGIC_NOT:
            self._lex.advance()
            node = self._parse_terminal()
            if node == None:
                return None
            return _ExpNode(_ExpNode.ID_BITWISE_NEG, node)
        elif tok == self._lex.TOK_LPAREN:
            self._lex.advance()
            node = self._parse_or()
            if node == None:
                return None
            tok = self._lex.peek()
            if tok != self._lex.TOK_RPAREN:
                return None
            self._lex.advance()
            return node
        else:
            return None


    # function _simplify_negate
    ###############################################################################
    def _simplify_negate(self, ptree, or_mask = _ExpNode.ALL_ZEROS, and_mask = _ExpNode.ALL_ONES):
        """
        Bitwise negate the input node and return a simplified expression.

        This funcion assumes the node is already simplified, so it will only
        reduce the topmost double negation, if any.
        """
        ptree.sanity_check()
        if ptree.node_type == _ExpNode.ID_BITWISE_NEG:
            return ptree.values
        elif ptree.node_type == _ExpNode.ID_INTEGER:
            return _ExpNode(_ExpNode.ID_INTEGER, ~ptree.values, ~and_mask, ~or_mask)
        return _ExpNode(_ExpNode.ID_BITWISE_NEG, ptree, ~and_mask, ~or_mask)


    # function _simplify_const
    ###############################################################################
    def _simplify_const(self, ptree, or_mask = _ExpNode.ALL_ZEROS, and_mask = _ExpNode.ALL_ONES):
        """
        Simplify constants in the parse tree.

        Parameters:
            ptree: the parse tree to simplify.

        Return:
            The simplified parse-(sub)-tree.
        """
        ptree.sanity_check()

        ptree.and_mask & and_mask
        ptree.or_mask = (ptree.or_mask | or_mask) & ptree.and_mask
        if ptree.or_mask == ptree.and_mask:
            return _ExpNode(_ExpNode.ID_INTEGER, ptree.or_mask)

        if ptree.node_type == _ExpNode.ID_INTEGER:
            ptree.values = (ptree.values | ptree.or_mask) & ptree.and_mask
            ptree.or_mask = ptree.values
            ptree.and_mask = ptree.values
            return ptree
        elif ptree.node_type == _ExpNode.ID_IDENTIFIER:
            return ptree
        elif ptree.node_type == _ExpNode.ID_BITWISE_NEG:
            # Recursive-descend and simplify sub-expressions.
            ptree.values = self._simplify_const(ptree.values, ~ptree.and_mask, ~ptree.or_mask)

            # Now simplify this level
            if ptree.values.node_type == _ExpNode.ID_INTEGER:
                return _ExpNode(_ExpNode.ID_INTEGER, ~ptree.values.values, ptree.or_mask, ptree.and_mask)
            if ptree.values.node_type == _ExpNode.ID_BITWISE_NEG:
                node = ptree.values.values
                return node
            return ptree
        elif ptree.node_type == _ExpNode.ID_BITWISE_AND:
            # Recursive-descend and simplify sub-expressions.
            ptree.values = [self._simplify_const(node, ptree.or_mask, ptree.and_mask) for node in ptree.values]

            # Simplify the masks
            ptree.or_mask |= functools.reduce(lambda a, x: a & x.or_mask, ptree.values, _ExpNode.ALL_ONES)
            ptree.and_mask &= functools.reduce(lambda a, x: a & x.and_mask, ptree.values, _ExpNode.ALL_ONES)

            # Now simplify this level
            ints = [node for node in ptree.values if node.node_type == _ExpNode.ID_INTEGER]
            nonints = [node for node in ptree.values if node.node_type != _ExpNode.ID_INTEGER]

            # Simplify multiple integers into one
            intval = functools.reduce(lambda a, x: a & x.values, ints, _ExpNode.ALL_ONES)
            intval = (intval | ptree.or_mask) & ptree.and_mask
            ptree.and_mask &= intval

            # Check if symbols can be simplified
            nonints_str = [node.to_string() for node in nonints]
            nonints_neg_str = [self._simplify_negate(node).to_string() for node in nonints]
            for i, j in itertools.combinations(range(len(nonints)), 2):
                if nonints_str[i] != None and nonints_str[j] != None:
                    if nonints_str[i] == nonints_str[j]:
                        nonints_str[i] = None
                    elif nonints_str[i] == nonints_neg_str[j]:
                        nonints_str[i] = None
                        nonints_str[j] = None
                        intval = _ExpNode.ALL_ZEROS
            ptree.values = [node for i, node in enumerate(nonints) if nonints_str[i] != None]
            ptree.values.sort(key = lambda node: node.to_string())

            # Prepare the return node
            if len(ptree.values) == 0:
                ptree.values = [_ExpNode(_ExpNode.ID_INTEGER, intval)]
            elif intval == _ExpNode.ALL_ZEROS:
                ptree.values = [_ExpNode(_ExpNode.ID_INTEGER, intval)]
            elif intval == _ExpNode.ALL_ONES:
                pass
            else:
                ptree.values.append(_ExpNode(_ExpNode.ID_INTEGER, intval))

            if len(ptree.values) == 1:
                return ptree.values[0]
            return ptree
        elif ptree.node_type == _ExpNode.ID_BITWISE_OR:
            # Recursive-descend and simplify sub-expressions.
            ptree.values = [self._simplify_const(node, ptree.or_mask, ptree.and_mask) for node in ptree.values]

            # Simplify the masks
            ptree.or_mask |= functools.reduce(lambda a, x: a | x.or_mask, ptree.values, _ExpNode.ALL_ZEROS)
            ptree.and_mask &= functools.reduce(lambda a, x: a | x.and_mask, ptree.values, _ExpNode.ALL_ZEROS)

            # Now simplify this level
            ints = [node for node in ptree.values if node.node_type == _ExpNode.ID_INTEGER]
            nonints = [node for node in ptree.values if node.node_type != _ExpNode.ID_INTEGER]

            # Simplify multiple integers into one
            intval = functools.reduce(lambda a, x: a | x.values, ints, _ExpNode.ALL_ZEROS)
            intval = (intval | ptree.or_mask) & ptree.and_mask
            ptree.or_mask |= intval

            # Check if symbols can be simplified
            nonints_str = [node.to_string() for node in nonints]
            nonints_neg_str = [self._simplify_negate(node).to_string() for node in nonints]
            for i, j in itertools.combinations(range(len(nonints)), 2):
                if nonints_str[i] != None and nonints_str[j] != None:
                    if nonints_str[i] == nonints_str[j]:
                        nonints_str[i] = None
                    elif nonints_str[i] == nonints_neg_str[j]:
                        nonints_str[i] = None
                        nonints_str[j] = None
                        intval = _ExpNode.ALL_ONES
            ptree.values = [node for i, node in enumerate(nonints) if nonints_str[i] != None]
            ptree.values.sort(key = lambda node: node.to_string())

            # Prepare the return node
            if len(ptree.values) == 0:
                ptree.values = [_ExpNode(_ExpNode.ID_INTEGER, intval)]
            elif intval == _ExpNode.ALL_ONES:
                ptree.values = [_ExpNode(_ExpNode.ID_INTEGER, intval)]
            elif intval == _ExpNode.ALL_ZEROS:
                pass
            else:
                ptree.values.append(_ExpNode(_ExpNode.ID_INTEGER, intval))

            if len(ptree.values) == 1:
                return ptree.values[0]
            return ptree
        elif ptree.node_type == _ExpNode.ID_BITWISE_XOR:
            # Recursive-descend and simplify sub-expressions.
            ptree.values = [self._simplify_const(node) for node in ptree.values]

            # Simplify the masks
            ptree.and_mask &= functools.reduce(lambda a, x: a | x.and_mask, ptree.values, _ExpNode.ALL_ZEROS)

            # Now simplify this level
            ints = [node for node in ptree.values if node.node_type == _ExpNode.ID_INTEGER]
            nonints = [node for node in ptree.values if node.node_type != _ExpNode.ID_INTEGER]

            # Simplify multiple integers into one
            intval = functools.reduce(lambda a, x: a ^ x.values, ints, _ExpNode.ALL_ZEROS)
            intval = (intval | ptree.or_mask) & ptree.and_mask
#            ptree.and_mask &= intval

            # Check if symbols can be simplified
            nonints_str = [node.to_string() for node in nonints]
            nonints_neg_str = [self._simplify_negate(node).to_string() for node in nonints]
            for i, j in itertools.combinations(range(len(nonints)), 2):
                if nonints_str[i] != None and nonints_str[j] != None:
                    if nonints_str[i] == nonints_str[j]:
                        nonints_str[i] = None
                        nonints_str[j] = None
                    elif nonints_str[i] == nonints_neg_str[j]:
                        nonints_str[i] = None
                        nonints_str[j] = None
                        intval ^= _ExpNode.ALL_ONES
            ptree.values = [node for i, node in enumerate(nonints) if nonints_str[i] != None]
            ptree.values.sort(key = lambda node: node.to_string())

            # Prepare the return node
            if len(ptree.values) == 0:
                return _ExpNode(_ExpNode.ID_INTEGER, intval)
            elif intval == _ExpNode.ALL_ZEROS:
                pass
            elif intval == _ExpNode.ALL_ONES:
                if len(ptree.values) == 1:
                    neg = _ExpNode(_ExpNode.ID_BITWISE_NEG, ptree.values[0])
                else:
                    neg = _ExpNode(_ExpNode.ID_BITWISE_NEG, ptree)
                return self._simplify_const(neg)
            else:
                ptree.values.append(_ExpNode(_ExpNode.ID_INTEGER, intval))

            if len(ptree.values) == 1:
                return ptree.values[0]
            return ptree
        elif ptree.node_type == _ExpNode.ID_LSHIFT:
            # Recursive-descend and simplify sub-expressions.
            or_mask = ptree.or_mask >> ptree.values[1].values if ptree.values[1].node_type == _ExpNode.ID_INTEGER else _ExpNode.ALL_ZEROS
            and_mask = ptree.and_mask >> ptree.values[1].values if ptree.values[1].node_type == _ExpNode.ID_INTEGER else _ExpNode.ALL_ONES
            ptree.values[0] = self._simplify_const(ptree.values[0], or_mask, and_mask)
            ptree.values[1] = self._simplify_const(ptree.values[1])

            # Now simplify this level
            if ptree.values[1].node_type == _ExpNode.ID_INTEGER:
                ptree.or_mask |= ptree.values[0].or_mask << ptree.values[1].values
                ptree.and_mask &= ptree.values[0].and_mask << ptree.values[1].values
                ptree.and_mask &= ptree.values[0].and_mask << ptree.values[1].values
                if ptree.values[0].node_type == _ExpNode.ID_INTEGER:
                    intval = ((ptree.values[0].values << ptree.values[1].values) | ptree.or_mask) & ptree.and_mask
                    ptree = _ExpNode(_ExpNode.ID_INTEGER, intval, ptree.or_mask, ptree.and_mask)
            if ptree.or_mask == ptree.and_mask:
                ptree = _ExpNode(_ExpNode.ID_INTEGER, ptree.or_mask)
            return ptree
        elif ptree.node_type == _ExpNode.ID_RSHIFT:
            # Recursive-descend and simplify sub-expressions.
            or_mask = ptree.or_mask << ptree.values[1].values if ptree.values[1].node_type == _ExpNode.ID_INTEGER else _ExpNode.ALL_ZEROS
            and_mask = ptree.and_mask << ptree.values[1].values if ptree.values[1].node_type == _ExpNode.ID_INTEGER else _ExpNode.ALL_ONES
            ptree.values[0] = self._simplify_const(ptree.values[0], or_mask, and_mask)
            ptree.values[1] = self._simplify_const(ptree.values[1])

            # Now simplify this level
            if ptree.values[1].node_type == _ExpNode.ID_INTEGER:
                ptree.or_mask |= ptree.values[0].or_mask >> ptree.values[1].values
                ptree.and_mask &= ptree.values[0].and_mask >> ptree.values[1].values
                if ptree.values[0].node_type == _ExpNode.ID_INTEGER:
                    intval = ((ptree.values[0].values >> ptree.values[1].values) | ptree.or_mask) & ptree.and_mask
                    ptree = _ExpNode(_ExpNode.ID_INTEGER, intval, ptree.or_mask, ptree.and_mask)
            if ptree.or_mask == ptree.and_mask:
                ptree = _ExpNode(_ExpNode.ID_INTEGER, ptree.or_mask)
            return ptree
        else:
            raise ValueError()
        return None


    # function simplify
    ###############################################################################
    def simplify(self, expr):
        """
        Simplify a C expression.

        Parameters:
            expr: a string with the C expression to simplify.

        Return:
            Returns a string with the simplified expression.

        The input string may contain any number of variables and any of the
        following operators: |, &, <<, >>.
        """
        # First, parse the expression.
        ptree = self._parse(expr)
        if ptree == None:
            return None

        old_exp_str = "0"
        exp_str = ptree.to_string()
        while exp_str != old_exp_str:
            old_exp_str = exp_str
            ptree = self._simplify_const(ptree)
            ptree.sanity_check()
            exp_str = ptree.to_string()

        return exp_str
