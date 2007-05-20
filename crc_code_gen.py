#  pycrc -- flexible CRC calculation utility and C source file generator
#
#  Copyright (c) 2006-2007  Thomas Pircher  <tehpeh@gmx.net>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.


"""
Code generator for pycrc.
use as follows:

   #from crc_opt import Options
   #opt = Options("0.6")
   #opt.parse(sys.argv)

This file is part of pycrc.
"""

from crc_symtable import SymbolTable
from crc_lexer import LangLexer, ExpLexer
import sys


# Class ParseError
###############################################################################
class ParseError(Exception):
    """
    The exception class for the parser
    """

    # __init__
    ###############################################################################
    def __init__(self, reason):
        self.reason = reason

    # __str__
    ###############################################################################
    def __str__(self):
        return self.reason


# Class CodeGenerator
###############################################################################
class CodeGenerator(object):
    """
    The code generator class
    """
    opt = None
    sym = None
    lex = LangLexer()
    explex = ExpLexer()

    mPrintMask      = 1
    mDoPrint        = 2
    mEvalElse       = 4

    # constructor
    ###############################################################################
    def __init__(self, opt):
        self.opt = opt
        self.sym = SymbolTable(opt)

    # parse
    #
    # the used grammar (more or less correctly) in Wirth Syntax Notation:
    #
    # DATA = { LITERAL | CONTROL } .
    # CONTROL = IF | "{%" LITERAL "%}" .
    # IF = "{%" "if" EXPRESSION "%}" DATA
    #       { "{%" "elif" EXPRESSION "%}" { DATA } }
    #       [ "{%" "else" "%}" { DATA } ]
    #       "{%" "endif" "%}" .
    # STRING = """" LITERAL """" .
    # ID = "{%" LITERAL "%}" .
    # LITERAL = letter { letter } .
    #
    # EXPRESSION = TERM { "or" TERM } .
    # TERM = FACTOR { "and" FACTOR } .
    # FACTOR = ( EXPRESSION ) | TERMINAL OP TERMINAL .
    # TERMINAL = ID | STRING | LITERAL .
    # OP = "==" | ">" | "<" | "<=" | "=>" | "!=" .
    #
    ###############################################################################
    def parse(self, str):
        """
        parse a string
        """
        self.lex.set_str(str)
        self.out_str = ""
        self.if_stack = [ self.mPrintMask | self.mDoPrint ]
        return self.__parse_data()

    # __parse_data
    ###############################################################################
    def __parse_data(self):
        """
        parse data
        """
        tok = self.lex.peek()
        while tok != self.lex.tok_EOF:
            if tok == self.lex.tok_text:
                if (self.if_stack[0] & self.mDoPrint) == self.mDoPrint:
                    self.out_str += self.lex.text
                self.lex.advance()
            elif tok == self.lex.tok_control:
                if (self.lex.text == "else") or (self.lex.text.startswith("elif ")) or (self.lex.text == "endif"):
                    if len(self.if_stack) == 0:
                        sys.stderr.write("Error: unexpected else of endif\n")
                        return False
                    return True
                if not self.__parse_control(self.lex.text):
                    return False
            else:
                sys.stderr.write("Error: unknown token %s\n" % self.lex.text)
                return False
            tok = self.lex.peek()
        return True

    # __parse_control
    ###############################################################################
    def __parse_control(self, str):
        """
        parse a control structure
        """
        tok = self.lex.peek()
        if tok == self.lex.tok_control:
            if self.lex.text.startswith("if"):
                if not self.__parse_if(self.lex.text):
                    sys.stderr.write("Error: if parsing failed\n")
                    return False
                self.lex.advance(skip_nl = True)
                if not self.__parse_data():
#                    sys.stderr.write("Error: No data for if\n")
                    return False
                while self.lex.text.startswith("elif "):
                    if not self.__parse_elif(self.lex.text):
                        sys.stderr.write("Error: elif parsing failed\n")
                        return False
                    self.lex.advance(skip_nl = True)
                    if not self.__parse_data():
                        sys.stderr.write("No data for elif\n")
                        return False
                if self.lex.text == "else":
                    if not self.__parse_else(self.lex.text):
                        sys.stderr.write("Error: else parsing failed\n")
                        return False
                    self.lex.advance(skip_nl = True)
                    if not self.__parse_data():
                        sys.stderr.write("No data for else\n")
                        return False
                if self.lex.text != "endif":
                    sys.stderr.write("missing endif\n")
                    return False
                if not self.__parse_endif(self.lex.text):
                    sys.stderr.write("endif parsing failed\n")
                    return False
                self.lex.advance(skip_nl = True)
                return True
            elif (self.lex.text == "else") or (self.lex.text.startswith("elif ")) or (self.lex.text == "endif"):
                sys.stderr.write("unexpected endif or else\n")
                return False
            else:
                if not self.__parse_literal(self.lex.text):
                    return False
                self.lex.advance()
                return True
        sys.stderr.write("unknown token in control\n")
        return False

    # __parse_if
    ###############################################################################
    def __parse_if(self, str):
        """
        parse a if operation
        """
        exp = str[3:].strip()
        try:
            condition = self.__parse_expression(exp)
        except ParseError:
            sys.stderr.write("parsing expression %s failed\n" % str)
            return False

        stack_state = self.if_stack[0]
        if (stack_state & self.mDoPrint) == self.mDoPrint:
            if condition:
                stack_state = self.mPrintMask | self.mDoPrint
            else:
                stack_state = self.mPrintMask | self.mEvalElse
        else:
            stack_state = 0
        self.if_stack.insert(0, stack_state)
        return True

    # __parse_elif
    ###############################################################################
    def __parse_elif(self, str):
        """
        parse a elif operation
        """
        stack_state = self.if_stack[0]
        if (stack_state & (self.mPrintMask | self.mEvalElse)) == (self.mPrintMask | self.mEvalElse):
            exp = str[5:].strip()
            try:
                condition = self.__parse_expression(exp)
            except ParseError:
                sys.stderr.write("parsing expression %s failed\n" % str)
                return False

            if condition:
                stack_state = self.mPrintMask | self.mDoPrint
            else:
                stack_state = self.mPrintMask | self.mEvalElse
        else:
            stack_state = 0

        self.if_stack[0] = stack_state
        return True

    # __parse_else
    ###############################################################################
    def __parse_else(self, str):
        """
        parse a if operation
        """
        stack_state = self.if_stack[0]
        if (stack_state & (self.mPrintMask | self.mEvalElse)) == (self.mPrintMask | self.mEvalElse):
            stack_state = self.mPrintMask | self.mDoPrint
        else:
            stack_state = 0
        self.if_stack[0] = stack_state
        return True

    # __parse_endif
    ###############################################################################
    def __parse_endif(self, str):
        """
        parse a endif operation
        """
        if len(self.if_stack) <= 1:
            sys.stderr.write("unexpected endif\n")
            return False
        self.if_stack.pop(0)
        return True

    # __parse_literal
    ###############################################################################
    def __parse_literal(self, str):
        """
        parse a literal
        """
        try:
            data = self.sym.getTerminal(str)
        except LookupError:
            sys.stderr.write("Error: unknown terminal %s\n" % self.lex.text)
            return False
        self.lex.advance()
        self.lex.prepend(data)
        return True

    # __parse_expression
    ###############################################################################
    def __parse_expression(self, str):
        """
        parse an expression
        """
        self.explex.set_str(str)
        try:
            ret = self.__parse_exp_exp()
        except ParseError:
            raise ParseError("Exp parsing failed")
        if self.explex.peek() != self.explex.tok_EOF:
            raise ParseError("extra characters after expression");
        return ret

    # __parse_exp_exp
    ###############################################################################
    def __parse_exp_exp(self):
        """
        parse an expression
        """
        ret = False

        while True:
            ret = self.__parse_exp_term() or ret

            tok = self.explex.peek()
            if tok == self.explex.tok_EOF:
                return ret
            if tok != self.explex.tok_or:
                print "expecting 'or' and not '%s'" % self.explex.text
                raise ParseError("Unexpected token")
            self.explex.advance()

        return False

    # __parse_exp_term
    ###############################################################################
    def __parse_exp_term(self):
        """
        parse a term
        """
        ret = True

        while True:
            ret = self.__parse_exp_factor() and ret
            tok = self.explex.peek()

            if tok != self.explex.tok_and:
                return ret
            self.explex.advance()

        return False

    # __parse_exp_factor
    ###############################################################################
    def __parse_exp_factor(self):
        """
        parse a term
        """
        ret = True

        tok = self.explex.peek()

        if tok == self.explex.tok_par_open:
            self.explex.advance()
            ret = self.__parse_exp_exp()
            tok = self.explex.peek()
            if tok != self.explex.tok_par_close:
                print "missing ')' before '%s'" % self.explex.text
                raise ParseError("missing ')' before '%s'" % self.explex.text)
            self.explex.advance()
            self.explex.peek()
            return ret

        val1_str = self.explex.text
        val1 = self.__parse_exp_terminal()
        tok = self.explex.peek()
        if tok != self.explex.tok_op:
            print "operator expected and not '%s' before '%s'" % (self.explex.text, self.explex.str)
            raise ParseError("operator expected and not '%s'" % self.explex.text)
        op_text = self.explex.text
        self.explex.advance()
        self.explex.peek()
        val2_str = self.explex.text
        val2 = self.__parse_exp_terminal()
        if val1 == None or val2 == None:
            if op_text == "==":
                if (val1 == None and val2 == "Undefined") or (val1 == "Undefined" and val2 == None):
                    return True
            elif op_text == "!=":
                if (val1 == None and val2 == "Undefined") or (val1 == "Undefined" and val2 == None):
                    return False
            if val1 == None:
                text = val1_str
            else:
                text = val2_str
            print "undefined parameter '%s'" % text
            raise ParseError("undefined parameter")

        val1_num = val2_num = None
        if val1 != None:
            if self.explex.is_int(val1):
                val1_num = int(val1)
            if self.explex.is_hex(val1):
                val1_num = int(val1, 16)
        if val2 != None:
            if self.explex.is_int(val2):
                val2_num = int(val2)
            if self.explex.is_hex(val2):
                val2_num = int(val2, 16)

        if val1_num != None and val2_num != None:
            val1 = val1_num
            val2 = val2_num

        try:
            if op_text == "<":
                return val1 < val2
            if op_text == "<=":
                return val1 <= val2
            if op_text == "==":
                return val1 == val2
            if op_text == "!=":
                return val1 != val2
            if op_text == ">=":
                return val1 >= val2
            if op_text == ">":
                return val1 > val2
            else:
                print "unknown operator '%s'" % op_text
                raise ParseError("unknown operator")
        except:
            raise ParseError("operator type mismatch")
        return False

    # __parse_exp_terminal
    ###############################################################################
    def __parse_exp_terminal(self):
        """
        parse a terminal
        """
        tok = self.explex.peek()
        if tok == self.explex.tok_id:
            if self.explex.text == "Undefined":
                ret = "Undefined"
            else:
                try:
                    ret = self.sym.getTerminal(self.explex.text)
                except LookupError:
                    ret = None
        elif tok == self.explex.tok_str:
            ret = self.explex.text
        else:
            print "unexpected terminal '%s' before '%s'" % (self.explex.text, self.explex.str)
            raise ParseError("unexpected terminal '%s'" % self.explex.text)
        self.explex.advance()
        return ret
