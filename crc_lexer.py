#  pycrc -- flexible CRC calculation utility and C source file generator
# -*- coding: Latin-1 -*-

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
Lexical analyzer for pycrc.
use as follows:

   #from crc_opt import Options
   #opt = Options("0.6")
   #opt.parse(sys.argv)

This file is part of pycrc.
"""

from crc_symtable import SymbolTable
import sys
import re


# Class Lexer
###############################################################################
class Lexer(object):
    """
    A lexical analyser
    """

    tok_unknown = 0
    tok_EOF     = 1

    # constructor
    ###############################################################################
    def __init__(self, str = ""):
        self.set_str(str)

    # set_str
    ###############################################################################
    def set_str(self, str):
        self.str = str
        self.text = ""
        self.text_len = 0
        self.tok = self.tok_unknown

    # peek
    ###############################################################################
    def peek(self):
        return self.tok_unknown

    # advance
    ###############################################################################
    def advance(self, skip_nl = False):
        skip_len = self.text_len
        if skip_nl and (len(self.str) > skip_len) and (self.str[skip_len] == "\n"):
            skip_len = skip_len + 1     # FIXME: check on Windoze if I can do simply a +1 to skip the line ending...
        self.str = self.str[skip_len:]

    # prepend
    ###############################################################################
    def prepend(self, str):
        self.text = ""
        self.text_len = 0
        self.str = str + self.str


# Class LangLexer
###############################################################################
class LangLexer(Lexer):
    """
    A lexical analyser
    """

    tok_text    = 12
    tok_control = 13

    # constructor
    ###############################################################################
    def __init__(self, str = ""):
        super(LangLexer, self).__init__(str)
        self.re_control = re.compile("\{%([^%}]*)%\}")

    # peek
    ###############################################################################
    def peek(self):
        if len(self.str) == 0:
            self.text = ""
            return self.tok_EOF
        m = self.re_control.search(self.str)
        if m == None:
            self.text = self.str
            self.text_len = len(self.text)
            return self.tok_text
        elif m.start() == 0:
            self.text = m.group(1)
            self.text_len = m.end()
            return self.tok_control
        else:
            self.text = m.string[:m.start()]
            self.text_len = m.start()
            return self.tok_text
        self.text = ""
        return self.tok_unknown


# Class ExpLexer
###############################################################################
class ExpLexer(Lexer):
    """
    A lexical analyser
    """

    tok_id          = 12
    tok_op          = 13
    tok_str         = 14
    tok_and         = 15
    tok_or          = 16
    tok_par_open    = 17
    tok_par_close   = 18

    # constructor
    ###############################################################################
    def __init__(self, str = ""):
        super(ExpLexer, self).__init__(str)
#        self.re_id = re.compile("\{%([^%}]+)%\}")
        self.re_id = re.compile("\\$([a-zA-Z][a-zA-Z0-9_-]*)")
        self.re_op = re.compile("<=|<|==|!=|>=|>")
#        self.re_str = re.compile("\"([^\"]+)\"")
#        self.re_str = re.compile("([a-zA-Z0-9_-]+)|\"([a-zA-Z0-9_-]+)\"")
        self.re_str = re.compile("\"?([a-zA-Z0-9_-]+)\"?")
        self.re_is_int = re.compile("^[-+]?[0-9]+$")
        self.re_is_hex = re.compile("^(0[xX])?[0-9a-fA-F]+$")

    # peek
    ###############################################################################
    def peek(self):
        self.str = self.str.strip()
        if len(self.str) == 0:
            self.text = ""
            return self.tok_EOF

        m = self.re_id.match(self.str)
        if m != None:
            self.text = m.group(1)
            self.text_len = m.end()
            return self.tok_id

        m = self.re_op.match(self.str)
        if m != None:
            self.text = m.string[:m.end()]
            self.text_len = m.end()
            return self.tok_op

        if self.str[:4] == "and ":
            self.text = "and"
            self.text_len = len(self.text)
            return self.tok_and

        if self.str[:3] == "or ":
            self.text = "or"
            self.text_len = len(self.text)
            return self.tok_or

        m = self.re_str.match(self.str)
        if m != None:
            self.text = m.group(1)
            self.text_len = m.end()
            return self.tok_str

        if self.str[0] == "(" or self.str[0] == ")":
            self.text = self.str[0]
            self.text_len = len(self.text)
            if self.str[0] == "(":
                return self.tok_par_open
            else:
                return self.tok_par_close

        self.text = ""
        return self.tok_unknown

    # is_int
    ###############################################################################
    def is_int(self, str):
        try:
            return self.re_is_int.search(str)
        except TypeError:
            return False

    # is_hex
    ###############################################################################
    def is_hex(self, str):
        try:
            return self.re_is_hex.match(str)
        except TypeError:
            return False
