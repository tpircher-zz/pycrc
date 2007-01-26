#!/usr/bin/env python

#  pycrc -- flexible CRC calculation utility and C source file generator
#  Copyright (C) 2006-2007  Thomas Pircher
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#  As a special exception, you may create a larger work that contains part
#  or all of the source code generated as output by pycrc and distribute
#  that work under terms of your choice.
#  Alternatively, if you modify or redistribute the pycrc script itself you
#  may (at your option) remove this special exception, which will cause the
#  resulting pycrc output files to be licensed under the GNU General Public
#  License without this special exception.


"""
pycrc is a flexible CRC calculation utility and C source file generator written in Python.

It can:
    -  generate the checksum out of a string
    -  generate the C header file and source for

It supports the following CRC algorithms:
    -  bit_by_bit       the basic algorithm which operates bit by bit on the augmented message.
    -  bit_by_bit_fast  a variation of the simple bit_by_bit algorithm.
    -  table_driven     the standard table driven algorithm.
"""

import sys
import os
from copy import copy
import string
from optparse import OptionParser, Option, OptionValueError
import time


"""
Bitmap of the algorithms
"""
Algo_Bit_by_Bit         = 0x01
Algo_Bit_by_Bit_Fast    = 0x02
Algo_Table_Driven       = 0x04


def check_hex(option, opt, value):
    """
    Checks if a value is given in a decimal integer of hexadecimal reppresentation.
    Returns the converted value or rises an exception on error.
    """
    try:
        if value.lower().startswith("0x"):
            return string.atoi(value, 16)
        else:
            return string.atoi(value)
    except ValueError:
        raise OptionValueError("option %s: invalid integer or hexadecimal value: %r" % (opt, value))


def check_bool(option, opt, value):
    """
    Checks if a value is given as a boolean value (either 0 or 1 or "true" or "false")
    Returns the converted value or rises an exception on error.
    """
    if value.isdigit():
        return string.atoi(value, 10) != 0
    elif value.lower() == "false":
        return False
    elif value.lower() == "true":
        return True
    else:
        raise OptionValueError("option %s: invalid boolean value: %r" % (opt, value))


class MyOption (Option):
    """
    New option parsing class extends the Option class
    """
    TYPES = Option.TYPES + ("hex", "bool")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["hex"] = check_hex
    TYPE_CHECKER["bool"] = check_bool


class Options:
    """
    The options parsing and validationg class
    """
    ProgramName     = "pycrc"
    Version         = "0.4"
    VersionStr      = "%s v%s" % (ProgramName, Version)
    WebAddress      = "http://www.tty1.net/pycrc/"
    Width           = None
    Poly            = None
    ReflectIn       = None
    XorIn           = None
    ReflectOut      = None
    XorOut          = None
    TableIdxBits    = 8
    Verbose         = False
    String          = "123456789"

    Algorithm       = 0x00
    SymbolPrefix    = None
    OutputFile      = None
    Action          = "check_string"

    def parse(self, argv = None):
        """
        Parses and validates the options given as arguments
        """
        parser = OptionParser(option_class=MyOption, usage="%prog [OPTIONS]", version=self.VersionStr)
        parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="print information about the model")
        parser.add_option("--algorithm",
                        action="store", type="string", dest="algorithm", default="all",
                        help="choose an algorithm from {bit_by_bit, bit_by_bit_fast, table_driven, all}", metavar="ALGO")
        parser.add_option("--model",
                        action="store", type="string", dest="model", default=None,
                        help="choose a parameter set from {crc-8, crc-16, citt, kermit, x-25, xmodem, zmodem, crc-32, crc-32c, posix, jam, xfer}", metavar="MODEL")
        parser.add_option("--width",
                        action="store", type="hex", dest="width",
                        help="use WIDTH bits", metavar="WIDTH")
        parser.add_option("--poly",
                        action="store", type="hex", dest="poly",
                        help="use HEX as Polynom", metavar="HEX")
        parser.add_option("--reflect_in",
                        action="store", type="bool", dest="reflect_in",
                        help="reflect input bytes", metavar="BOOL")
        parser.add_option("--xor_in",
                        action="store", type="hex", dest="xor_in",
                        help="use HEX as initial value", metavar="HEX")
        parser.add_option("--reflect_out",
                        action="store", type="bool", dest="reflect_out",
                        help="reflect output bytes", metavar="BOOL")
        parser.add_option("--xor_out",
                        action="store", type="hex", dest="xor_out",
                        help="xor the final crc value with HEX", metavar="HEX")
        parser.add_option("--table_idx_with",
                        action="store", type="int", dest="table_idx_with",
                        help="use WIDTH bits to index the crc table; WIDTH one of {1, 2, 4, 8}", metavar="WIDTH")
        parser.add_option("--check_string",
                        action="store", type="string", dest="check_string",
                        help="calculate the checksum of the given string ('123456789' default)", metavar="STRING")
        parser.add_option("--check_file",
                        action="store", type="string", dest="check_file",
                        help="calculate the checksum of the given file", metavar="FILE")
        parser.add_option("--generate_c",
                        action="store_true", dest="generate_c", default=False,
                        help="generate a C source file")
        parser.add_option("--generate_c_main",
                        action="store_true", dest="generate_c_main", default=False,
                        help="generate a C source file with main function")
        parser.add_option("--generate_h",
                        action="store_true", dest="generate_h", default=False,
                        help="generate a C header source file")
        parser.add_option("--symbol_prefix",
                        action="store", type="string", dest="symbol_prefix",
                        help="when generating source code, use STRING as prefix to the generated symbols", metavar="STRING")
        parser.add_option("-o", "--output_file",
                        action="store", type="string", dest="output_file",
                        help="write the generated code to file instead to stdout", metavar="FILE")

        (options, args) = parser.parse_args()

        if options.model != None:
            mod = options.model.lower();
            if   mod == "crc-8":
                self.Width      = 8
                self.Poly       = 0x07
                self.ReflectIn  = False
                self.XorIn      = 0x0
                self.ReflectOut = False
                self.XorOut     = 0x0
            elif mod == "crc-16":
                self.Width      = 16
                self.Poly       = 0x8005
                self.ReflectIn  = True
                self.XorIn      = 0x0
                self.ReflectOut = True
                self.XorOut     = 0x0
            elif mod == "citt":
                self.Width      = 16
                self.Poly       = 0x1021
                self.ReflectIn  = False
                self.XorIn      = 0xffff
                self.ReflectOut = False
                self.XorOut     = 0x0
            elif mod == "kermit":
                self.Width      = 16
                self.Poly       = 0x1021
                self.ReflectIn  = True
                self.XorIn      = 0x0
                self.ReflectOut = True
                self.XorOut     = 0x0
            elif mod == "x-25":
                self.Width      = 16
                self.Poly       = 0x1021
                self.ReflectIn  = True
                self.XorIn      = 0xffff
                self.ReflectOut = True
                self.XorOut     = 0xffff
            elif mod == "xmodem":
                self.Width      = 16
                self.Poly       = 0x8408
                self.ReflectIn  = True
                self.XorIn      = 0x0
                self.ReflectOut = True
                self.XorOut     = 0x0
            elif mod == "zmodem":
                self.Width      = 16
                self.Poly       = 0x1021
                self.ReflectIn  = False
                self.XorIn      = 0x0
                self.ReflectOut = False
                self.XorOut     = 0x0
            elif mod == "crc-32":
                self.Width      = 32
                self.Poly       = 0x4c11db7
                self.ReflectIn  = True
                self.XorIn      = 0xffffffff
                self.ReflectOut = True
                self.XorOut     = 0xffffffff
            elif mod == "crc-32c":
                self.Width      = 32
                self.Poly       = 0x1edc6f41
                self.ReflectIn  = True
                self.XorIn      = 0xffffffff
                self.ReflectOut = True
                self.XorOut     = 0xffffffff
            elif mod == "posix":
                self.Width      = 32
                self.Poly       = 0x4c11db7
                self.ReflectIn  = False
                self.XorIn      = 0x0
                self.ReflectOut = False
                self.XorOut     = 0xffffffff
            elif mod == "jam":
                self.Width      = 32
                self.Poly       = 0x4c11db7
                self.ReflectIn  = True
                self.XorIn      = 0xffffffff
                self.ReflectOut = True
                self.XorOut     = 0x0
            elif mod == "xfer":
                self.Width      = 32
                self.Poly       = 0x000000af
                self.ReflectIn  = False
                self.XorIn      = 0x0
                self.ReflectOut = False
                self.XorOut     = 0x0
            else:
                sys.stderr.write("Error: unsupported model %s\n" % options.model)
                sys.exit(1)

        if options.width != None:
            self.Width          = options.width
        if options.poly != None:
            self.Poly           = options.poly
        if options.reflect_in != None:
            self.ReflectIn      = options.reflect_in
        if options.xor_in != None:
            self.XorIn          = options.xor_in
        if options.reflect_out != None:
            self.ReflectOut     = options.reflect_out
        if options.xor_out != None:
            self.XorOut         = options.xor_out
        if options.table_idx_with != None:
            if options.table_idx_with == 1 or \
                    options.table_idx_with == 2 or \
                    options.table_idx_with == 4 or \
                    options.table_idx_with == 8:
                self.TableIdxBits   = options.table_idx_with
            else:
                sys.stderr.write("Error: unsupported table_idx_with %d\n" % options.table_idx_with)
                sys.exit(1)

        if self.Width != None:
            self.MSB_Mask = 0x1 << (self.Width - 1)
            self.Mask = ((self.MSB_Mask - 1) << 1) | 1
            if self.Poly != None:
                self.Poly = self.Poly & self.Mask
            if self.XorIn != None:
                self.XorIn = self.XorIn & self.Mask
            if self.XorOut != None:
                self.XorOut = self.XorOut & self.Mask
        else:
            self.MSB_Mask = None
            self.Mask = None

        if self.Width       == None or \
                self.Poly       == None or \
                self.ReflectIn  == None or \
                self.XorIn      == None or \
                self.ReflectOut == None or \
                self.XorOut     == None:
            self.UndefinedCrcParameters = True
        else:
            self.UndefinedCrcParameters = False

        if options.algorithm != None:
            alg = options.algorithm.lower()
            if alg == "bit_by_bit" or alg == "all":
                self.Algorithm      |= Algo_Bit_by_Bit
            if alg == "bit_by_bit_fast"  or alg == "all":
                self.Algorithm      |= Algo_Bit_by_Bit_Fast
            if alg == "table_driven" or alg == "all":
                self.Algorithm      |= Algo_Table_Driven
            if self.Algorithm == 0:
                sys.stderr.write("Error: unknown algorithm %s\n" % options.algorithm)
                sys.exit(1)
        if self.Width != None and (self.Width % 8) != 0:
            if options.algorithm == "bit_by_bit_fast" or options.algorithm == "table_driven":
                sys.stderr.write("Error: width non aligned to byte boundaries, algorithm %s not applicable\n" % options.algorithm)
                sys.exit(1)
            else:
                self.Algorithm &= ~(Algo_Bit_by_Bit_Fast | Algo_Table_Driven)
        if self.Width != None and self.Width < 8:
            if options.algorithm == "table_driven":
                sys.stderr.write("Error: width < 8, algorithm %s not applicable\n" % options.algorithm)
                sys.exit(1)
            else:
                self.Algorithm &= ~(Algo_Table_Driven)

        if options.symbol_prefix != None:
            self.SymbolPrefix = options.symbol_prefix
        if options.output_file != None:
            self.OutputFile = options.output_file
        op_count = 0
        if options.check_string != None:
            self.Action         = "check_string"
            self.CheckString    = options.check_string
            op_count += 1
        if options.check_file != None:
            self.Action         = "check_file"
            self.CheckFile      = options.check_file
            op_count += 1
        if options.generate_c or options.generate_c_main or options.generate_h:
            if self.Algorithm != Algo_Bit_by_Bit and self.Algorithm != Algo_Bit_by_Bit_Fast and self.Algorithm != Algo_Table_Driven:
                sys.stderr.write("Error: select an algorithm to be used in the generated file\n")
                sys.exit(1)
        if options.generate_c:
            self.Action         = "generate_c"
            op_count += 1
        if options.generate_c_main:
            self.Action         = "generate_c_main"
            op_count += 1
        if options.generate_h:
            self.Action         = "generate_h"
            op_count += 1
        if op_count == 0:
            self.Action         = "check_string"
        if op_count > 1:
            sys.stderr.write("Error: too many actions scecified\n")
            sys.exit(1)

        self.Verbose            = options.verbose


def reflect(data, width):
    """
    reflects a data word, i.e. reverts the bit order
    """
    x = 0
    for i in range(width):
        x = x | (((data >> (width - i -1)) & 1) << i)
    return x

def crc_handle_bit(opt, register, new_bit):
    """
    This function is part of the crc_bit_by_bit algorithm.
    This function takes one bit from the augmented message as argument and returns the new crc value
    """
    register_msb = register & opt.MSB_Mask
    register = (register << 1) & opt.Mask
    if new_bit != 0:
        register = register | 1
    if register_msb != 0:
        register = register ^ opt.Poly
    return register & opt.Mask

def crc_bit_by_bit(opt, str):
    """
    Classic simple and slow CRC implementation.
    This function iterates bit by bit over the augmented input message and returns the calculated CRC value at the end
    """
    register = opt.XorIn
    for j in range(opt.Width):
        bit = register & 1
        if bit != 0:
            register = ((register ^ opt.Poly) >> 1) | opt.MSB_Mask
        else:
            register = register >> 1
    register &= opt.Mask

    for i in range(len(str)):
        octet = ord(str[i])
        if opt.ReflectIn:
            octet = reflect(octet, 8)
        for j in range(8):
            new_bit = octet & (0x80 >> j)
            register = crc_handle_bit(opt, register, new_bit)
    for j in range(opt.Width):
        register = crc_handle_bit(opt, register, 0)

    if opt.ReflectOut:
        register = reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register


def crc_bit_by_bit_fast(opt, str):
    """
    This is a slightly modified version of the bit_by_bit algorithm: it does not need to loop over the augmented bit,
    i.e. the Width 0-bits wich are appended to the input message in the bit_by_bit algorithm.
    """
    register = opt.XorIn

    for i in range(len(str)):
        octet = ord(str[i])
        if opt.ReflectIn:
            octet = reflect(octet, 8)
        for j in range(8):
            bit = register & opt.MSB_Mask
            register <<= 1
            if octet & (0x80 >> j):
                bit ^= opt.MSB_Mask
            if bit:
                register ^= opt.Poly
        register &= opt.Mask
    if opt.ReflectOut:
        register = reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register


def crc_gen_table(opt):
    """
    This function generates the CRC table used for the table_driven CRC algorithm.
    """
    tbl = {}
    for i in range(1 << opt.TableIdxBits):
        register = i
        if opt.ReflectIn:
            register = reflect(register, opt.TableIdxBits)
        register = register << (opt.Width - opt.TableIdxBits)
        for j in range(opt.TableIdxBits):
            if register & opt.MSB_Mask != 0:
                register = (register << 1) ^ opt.Poly
            else:
                register = (register << 1)
        if opt.ReflectIn:
            register = reflect(register, opt.Width)
        tbl[i] = register & opt.Mask
    return tbl


def crc_table_driven(opt, str):
    """
    The Standard table_driven CRC algorithm.
    """
    tbl = crc_gen_table(opt)

    if not opt.ReflectIn:
        register = opt.XorIn
        for i in range(len(str)):
            octet = ord(str[i])
            tblidx = ((register >> (opt.Width - 8)) ^ octet) & 0xff
            register = ((register << 8) ^ tbl[tblidx]) & opt.Mask
    else:
        register = reflect(opt.XorIn, opt.Width)
        for i in range(len(str)):
            octet = ord(str[i])
            tblidx = (register ^ octet) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & opt.Mask
        register = reflect(register, opt.Width)

    if opt.ReflectOut:
        register = reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register


class CRenderer:
    """
    This class generates a .c or .h source file
    """

    def __init__(self, opt):
        """
        Initialise the local variables.
        In particular, copy all used parameters from the opt class and pretty-print them
        """
        self.ProgramName    = opt.ProgramName
        self.Version        = opt.Version
        self.VersionStr     = opt.VersionStr
        self.WebAddress     = opt.WebAddress
        self.Width          = opt.Width
        self.Poly           = opt.Poly
        self.ReflectIn      = opt.ReflectIn
        self.XorIn          = opt.XorIn
        self.ReflectOut     = opt.ReflectOut
        self.XorOut         = opt.XorOut
        self.MSB_Mask       = opt.MSB_Mask
        self.Mask           = opt.Mask
        self.Algorithm      = opt.Algorithm
        self.SymbolPrefix   = opt.SymbolPrefix
        self.OutputFile     = opt.OutputFile
        self.Action         = opt.Action
        self.UndefinedCrcParameters = opt.UndefinedCrcParameters
        self.TableIdxBits   = opt.TableIdxBits        # 8: 256, 4: 16, 2: 4

        if self.Width == None or \
                self.XorIn      == None or \
                self.ReflectIn  == None:
            self.ConstantCrcInit = False
        else:
            self.ConstantCrcInit = True

        if self.ReflectOut != None and self.Algorithm == Algo_Table_Driven:
            self.StaticReflectFunc = False
        elif self.ReflectOut != None and self.Algorithm == Algo_Bit_by_Bit_Fast:
            self.StaticReflectFunc = False
        else:
            self.StaticReflectFunc = True

        if self.Algorithm == Algo_Bit_by_Bit_Fast or self.Algorithm == Algo_Table_Driven:
            if self.Width != None and self.ReflectOut != None and self.XorOut != None:
                self.InlineFinalizeFunc = True
            else:
                self.InlineFinalizeFunc = False
        else:
            self.InlineFinalizeFunc = False

        if self.SymbolPrefix == None:
            self.SymbolPrefix = "crc"

        if self.OutputFile == None:
            self.OutputFile = "stdout"

        if self.Width == None:
            self.crc_typedef = "unsigned long"
        elif self.Width <= 8:
            self.crc_typedef = "uint8_t"
        elif self.Width <= 16:
            self.crc_typedef = "uint16_t"
        elif self.Width <= 32:
            self.crc_typedef = "uint32_t"
        else:
            self.crc_typedef = "unsigned long"

        if opt.Width != None:
            self.PrettyWidth        = "%d" % opt.Width
        else:
            self.PrettyWidth        = "cfg->width"
        if opt.Poly != None:
            self.PrettyPoly         = self.__pretty_hex(opt.Poly, opt.Width)
        else:
            self.PrettyPoly         = "cfg->poly"
        if opt.ReflectIn != None:
            self.PrettyReflectIn    = self.__pretty_bool(opt.ReflectIn)
        else:
            self.PrettyReflectIn    = "cfg->reflect_in"
        if opt.XorIn != None:
            self.PrettyXorIn        = self.__pretty_hex(opt.XorIn, opt.Width)
        else:
            self.PrettyXorIn        = "cfg->xor_in"
        if opt.ReflectOut != None:
            self.PrettyReflectOut   = self.__pretty_bool(opt.ReflectOut)
        else:
            self.PrettyReflectOut   = "cfg->reflect_out"
        if opt.XorOut != None:
            self.PrettyXorOut       = self.__pretty_hex(opt.XorOut, opt.Width)
        else:
            self.PrettyXorOut       = "cfg->xor_out"
        if opt.MSB_Mask != None:
            self.PrettyMSB_Mask     = self.__pretty_hex(opt.MSB_Mask, opt.Width)
        else:
            self.PrettyMSB_Mask     = "cfg->msb_mask"
        if opt.Mask != None:
            self.PrettyMask         = self.__pretty_hex(opt.Mask, opt.Width)
        else:
            self.PrettyMask         = "cfg->crc_mask"

        self.TableWidth         = 1 << self.TableIdxBits
        self.PrettyTableWidth   = "%d" % self.TableWidth
        self.PrettyTableMask    = self.__pretty_hex(self.TableWidth - 1, 8)
        self.PrettyTableInit    = self.__get_table(opt)
        self.PrettyInitValue    = self.__get_init_value()
        self.PrettyAlgorithm    = self.__pretty_algorithm()
        self.GenDate = time.asctime()
        self.HeaderProtection = self.__pretty_hdrprotection()
        if self.OutputFile.endswith(".c"):
            self.PrettyHeaderFile = self.OutputFile[0:-1] + "h"
        else:
            self.PrettyHeaderFile = self.OutputFile + ".h"
        self.PrettyCrc_t            = self.SymbolPrefix + "_t"
        self.PrettyCrcCfg_t         = self.SymbolPrefix + "_cfg_t"
        self.PrettyCrcReflectFunc   = self.SymbolPrefix + "_reflect"
        self.PrettyCrcGenTableFunc  = self.SymbolPrefix + "_table_gen"
        self.PrettyCrcInitFunc      = self.SymbolPrefix + "_init"
        self.PrettyCrcUpdateFunc    = self.SymbolPrefix + "_update"
        self.PrettyCrcFinalizeFunc  = self.SymbolPrefix + "_finalize"


    def print_param(self):
        """
        Generate a string with the options pretty-printed (used in the --verbose mode
        """
        out  = ""
        if self.Width != None:
            out += "Width        = %s\n" % self.PrettyWidth
        else:
            out += "Width        = %s\n" % "Undefined"
        if self.Poly != None:
            out += "Poly         = %s\n" % self.PrettyPoly
        else:
            out += "Poly         = %s\n" % "Undefined"
        if self.ReflectIn != None:
            out += "ReflectIn    = %s\n" % self.PrettyReflectIn
        else:
            out += "ReflectIn    = %s\n" % "Undefined"
        if self.XorIn != None:
            out += "XorIn        = %s\n" % self.PrettyXorIn
        else:
            out += "XorIn        = %s\n" % "Undefined"
        if self.ReflectOut != None:
            out += "ReflectOut   = %s\n" % self.PrettyReflectOut
        else:
            out += "ReflectOut   = %s\n" % "Undefined"
        if self.XorOut != None:
            out += "XorOut       = %s\n" % self.PrettyXorOut
        else:
            out += "XorOut       = %s\n" % "Undefined"
        out += "Algorithm    = %s\n" % self.PrettyAlgorithm
        return out

    def __pretty_hex(self, value, width = None):
        """
        Return a value of width bits as a pretty hexadecimal formatted string.
        """
        #if value == 0:
        #    return "0x0"
        if width == None:
            return "0x%x" % value
        width = (width + 3) / 4
        str = "0x%%0%dx" % width
        return str % value

    def __pretty_bool(self, value):
        """
        Return a boolen value of width bits as a pretty formatted string.
        """
        if value:
            return "True"
        else:
            return "False"

    def __pretty_hdrprotection(self):
        """
        Return the name of a C header protection (e.g. __CRC_IMPLEMENTATION_H__)
        """
        tr_str = ""
        for i in range(256):
            if chr(i).isalpha():
                tr_str += chr(i).upper()
            else:
                tr_str += '_'
        str = self.OutputFile
        str = os.path.basename(str)
        str = str.upper()
        str = str.translate(tr_str)
        return "__" + str + "__"

    def __pretty_algorithm(self):
        """
        Return the selected algorithm(s) in a nicely formatted string
        """
        alg = []
        if self.Algorithm & Algo_Bit_by_Bit:
            alg += ["bit_by_bit"]
        if self.Algorithm & Algo_Bit_by_Bit_Fast:
            alg += ["bit_by_bit_fast"]
        if self.Algorithm & Algo_Table_Driven:
            alg += ["table_driven"]
        return " | ".join(alg)

    def __get_init_value(self):
        """
        Return the init value of a C implementation, according to the selected algorithm and
        to the given options
        If no default option is given for a given parameter, value in the cfg_t structure must be used.
        """
        if not self.ConstantCrcInit:
            return None
        if self.Algorithm != Algo_Bit_by_Bit and self.Algorithm != Algo_Bit_by_Bit_Fast and self.Algorithm != Algo_Table_Driven:
            init = 0
        elif self.Algorithm == Algo_Bit_by_Bit:
            register = self.XorIn
            for j in range(self.Width):
                bit = register & 1
                if bit != 0:
                    register = ((register ^ self.Poly) >> 1) | self.MSB_Mask
                else:
                    register = register >> 1
            init = register & self.Mask
        elif self.Algorithm == Algo_Bit_by_Bit_Fast:
            init = self.XorIn
        elif self.Algorithm == Algo_Table_Driven:
            if self.ReflectIn:
                init = reflect(self.XorIn, self.Width)
            else:
                init = self.XorIn
        else:
            init = 0
        return self.__pretty_hex(init, self.Width)

    def __get_table(self, opt):
        """
        Return the precalculated CRC table for the table_driven implementation
        """
        if self.Algorithm != Algo_Table_Driven:
            return "{ 0 }"
        if self.UndefinedCrcParameters:
            return "{ 0 }"
        tbl = crc_gen_table(opt)
        if self.Width >= 32:
            values_per_line = 4
        elif self.Width >= 16:
            values_per_line = 8
        else:
            values_per_line = 16
        out  = ""
        out += "{\n"
        for i in range(self.TableWidth):
            if i % values_per_line == 0:
                out += "    "
            if i == (self.TableWidth - 1):
                out += "%s\n" % self.__pretty_hex(tbl[i], self.Width)
            elif i % values_per_line == (values_per_line - 1):
                out += "%s,\n" % self.__pretty_hex(tbl[i], self.Width)
            else:
                out += "%s, " % self.__pretty_hex(tbl[i], self.Width)
        out += "}"
        return out

    def __pretty_file_hdr(self):
        """
        Return the header banner of the generated .c or .h file
        """
        out  = ""
        out += "/**\n"
        out += " * \\file %s\n" % (self.OutputFile)
        out += " * Functions and types for CRC checks.\n"
        out += " *\n"
        out += " * Generated on %s,\n" % (self.GenDate)
        out += " * by %s, %s\n" % (self.VersionStr, self.WebAddress)
        out += " * using the configuration:\n"
        if self.Width != None:
            out += " *    Width        = %s\n" % (self.PrettyWidth)
        else:
            out += " *    Width        = %s\n" % "Undefined"
        if self.Poly != None:
            out += " *    Poly         = %s\n" % (self.PrettyPoly)
        else:
            out += " *    Poly         = %s\n" % "Undefined"
        if self.XorIn != None:
            out += " *    XorIn        = %s\n" % (self.PrettyXorIn)
        else:
            out += " *    XorIn        = %s\n" % "Undefined"
        if self.ReflectIn != None:
            out += " *    ReflectIn    = %s\n" % (self.PrettyReflectIn)
        else:
            out += " *    ReflectIn    = %s\n" % "Undefined"
        if self.XorOut != None:
            out += " *    XorOut       = %s\n" % (self.PrettyXorOut)
        else:
            out += " *    XorOut       = %s\n" % "Undefined"
        if self.ReflectOut != None:
            out += " *    ReflectOut   = %s\n" % (self.PrettyReflectOut)
        else:
            out += " *    ReflectOut   = %s\n" % "Undefined"
        out += " *    Algorithm    = %s\n" % (self.__pretty_algorithm())
        out += " *****************************************************************************/\n"
        return out

    def __pretty_crc_reflect_doc(self):
        """
        Return the doxygen header for the crc_reflect function
        """
        out = ""
        out += "/**\n"
        out += " * \\brief      Reflect all bits of a \\a data word of \\a data_len bytes.\n"
        out += " * \\param data         The data word to be reflected.\n"
        out += " * \\param data_len     The width of \\a data expressed in number of bits.\n"
        out += " * \\return     The reflected data.\n"
        out += " *****************************************************************************/\n"
        return out

    def __pretty_crc_table_gen_doc(self):
        """
        Return the doxygen header for the crc_table_gen function
        """
        out = ""
        out += "/**\n"
        out += " * \\brief      Populate the private static crc table.\n"
        out += " * \\param cfg  A pointer to a initialised %s structure.\n" % (self.PrettyCrcCfg_t)
        out += " * \\return     void\n"
        out += " *****************************************************************************/\n"
        return out

    def __pretty_crc_init_doc(self):
        """
        Return the doxygen header for the crc_init function
        """
        out = ""
        out += "/**\n"
        out += " * \\brief      Calculate the initial crc value.\n"
        if not self.ConstantCrcInit:
            out += " * \\param cfg  A pointer to a initialised %s structure.\n" % (self.PrettyCrcCfg_t)
        out += " * \\return     The initial crc value.\n"
        out += " *****************************************************************************/\n"
        return out

    def __pretty_crc_update_doc(self):
        """
        Return the doxygen header for the crc_update function
        """
        out = ""
        out += "/**\n"
        out += " * \\brief          Update the crc value with new data.\n"
        out += " * \\param crc      The current crc value.\n"
        if not self.ConstantCrcInit:
            out += " * \\param cfg      A pointer to a initialised %s structure.\n" % (self.PrettyCrcCfg_t)
        out += " * \\param data     Pointer to a buffer of \\a data_len bytes.\n"
        out += " * \\param data_len Number of bytes in the \\a data buffer.\n"
        out += " * \\return         The updated crc value.\n"
        out += " *****************************************************************************/\n"
        return out

    def __pretty_crc_finalize_doc(self):
        """
        Return the doxygen header for the crc_finalize function
        """
        out = ""
        out += "/**\n"
        out += " * \\brief      Calculate the final crc value.\n"
        if self.UndefinedCrcParameters:
            out += " * \\param cfg  A pointer to a initialised %s structure.\n" % (self.PrettyCrcCfg_t)
        out += " * \\param crc  The current crc value.\n"
        out += " * \\return     The final crc value.\n"
        out += " *****************************************************************************/\n"
        return out

    def __generate_h(self):
        """
        Return the source code for a .h file
        """
        out  = ""
        out += self.__pretty_file_hdr()
        out += "#ifndef %s\n" % (self.HeaderProtection)
        out += "#define %s\n" % (self.HeaderProtection)
        out += "\n"
        out += "#include <stdint.h>\n"
        out += "#include <unistd.h>\n"
        if self.UndefinedCrcParameters:
            out += "#include <stdbool.h>\n"
        out += "\n"
        out += "/**\n"
        out += " * \\brief   The definition of the used algorithm.\n"
        out += " *****************************************************************************/\n"
        if self.Algorithm & Algo_Bit_by_Bit:
            out += "#define CRC_ALGO_BIT_BY_BIT 1\n"
        if self.Algorithm & Algo_Bit_by_Bit_Fast:
            out += "#define CRC_ALGO_BIT_BY_BIT_FAST 1\n"
        if self.Algorithm & Algo_Table_Driven:
            out += "#define CRC_ALGO_TABLE_DRIVEN 1\n"
        out += "\n"
        out += "/**\n"
        out += " * \\brief   The type of the CRC values.\n"
        out += " *\n"
        out += " * This type must be big enough to contain at least %s bits.\n" % (self.PrettyWidth)
        out += " *****************************************************************************/\n"
        out += "typedef %s %s;\n" % (self.crc_typedef, self.PrettyCrc_t)
        out += "\n"
        # crc_cfg_t
        if self.UndefinedCrcParameters:
            out += "/**\n"
            out += " * \\brief   The configuration type of the CRC algorithm.\n"
            out += " *****************************************************************************/\n"
            out += "typedef struct {\n"
            if self.Width == None:
                out += "    unsigned int width;     /*!< The width of the polynom */\n"
            if self.Poly == None:
                out += "    %s poly;             /*!< The CRC polynom */\n" % (self.PrettyCrc_t)
            if self.ReflectIn == None:
                out += "    bool reflect_in;        /*!< Whether the input shall be reflected or not */\n"
            if self.XorIn == None:
                out += "    %s xor_in;           /*!< The initial value of the algorithm */\n" % (self.PrettyCrc_t)
            if self.ReflectOut == None:
                out += "    bool reflect_out;       /*!< Wether the output shall be reflected or not */\n"
            if self.XorOut == None:
                out += "    %s xor_out;          /*!< The value which shall be XOR-ed to the final CRC value */\n" % (self.PrettyCrc_t)
            if self.Width == None:
                out += "\n"
                out += "    // internal parameters\n"
                out += "    %s msb_mask;         /*!< A bitmask with the Most Significant Bit set to 1\n" % (self.PrettyCrc_t)
                out += "                                 Initialise as 0x01 << (%s - 1) */\n" % (self.PrettyWidth)
                out += "    %s crc_mask;         /*!< A bitmask with all %s bits set to 1\n" % (self.PrettyCrc_t, self.PrettyWidth)
                out += "                                 Initialise as (cfg->msb_mask - 1) | cfg->msb_mask */\n"
            out += "} %s;\n" % (self.PrettyCrcCfg_t)
            out += "\n"
        # crc_reflect
        if self.ReflectIn or self.ReflectOut:
            if not self.StaticReflectFunc:
                out += self.__pretty_crc_reflect_doc()
                out += "long %s(long data, size_t data_len);\n" % (self.PrettyCrcReflectFunc)
                out += "\n"
        # crc_table_gen
        if self.Algorithm == Algo_Table_Driven:
            if self.UndefinedCrcParameters:
                out += self.__pretty_crc_table_gen_doc()
                out += "void %s(const %s *cfg);\n" %(self.PrettyCrcGenTableFunc, self.PrettyCrcCfg_t)
            out += "\n"
        # crc_init
        out += self.__pretty_crc_init_doc()
        if not self.ConstantCrcInit:
            out += "%s %s(const %s *cfg);\n" % (self.PrettyCrc_t, self.PrettyCrcInitFunc, self.PrettyCrcCfg_t)
        else:
            out += "static inline %s %s(void)\n" % (self.PrettyCrc_t, self.PrettyCrcInitFunc)
            out += "{\n"
            out += "    return %s;\n" % (self.PrettyInitValue)
            out += "}\n"
        out += "\n"
        # crc_update
        out += self.__pretty_crc_update_doc()
        if self.UndefinedCrcParameters:
            out += "%s %s(const %s *cfg, %s crc, const unsigned char *data, size_t data_len);\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
        else:
            out += "%s %s(%s crc, const unsigned char *data, size_t data_len);\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrc_t)
        out += "\n"
        # crc_finalize
        out += self.__pretty_crc_finalize_doc()
        if self.InlineFinalizeFunc:
            out += "static inline %s %s(%s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrc_t)
            out += "{\n"
            if self.ReflectOut:
                out += "    return %s(crc, %s) ^ %s;\n" % (self.PrettyCrcReflectFunc, self.Width, self.XorOut)
            else:
                out += "    return crc ^ %s;\n" % (self.XorOut)
            out += "}\n"
        if self.UndefinedCrcParameters:
            out += "%s %s(const %s *cfg, %s crc);\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
        elif self.Algorithm == Algo_Bit_by_Bit:
            out += "%s %s(%s crc);\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrc_t)
        out += "\n"
        out += "#endif  // %s\n" % self.HeaderProtection
        return out

    def __generate_c(self):
        """
        Return the source code for a .c file
        """
        out  = ""
        out += self.__pretty_file_hdr()
        out += "#include \"%s\"\n" % self.PrettyHeaderFile
        out += "#include <stdint.h>\n"
        out += "#include <unistd.h>\n"
        if self.UndefinedCrcParameters or self.Algorithm == Algo_Bit_by_Bit or self.Algorithm == Algo_Bit_by_Bit_Fast:
            out += "#include <stdbool.h>\n"
        out += "\n"
        if self.StaticReflectFunc:
            out += "static long %s(long data, size_t data_len);\n" % (self.PrettyCrcReflectFunc)
        else:
            out += "long %s(long data, size_t data_len);\n" % (self.PrettyCrcReflectFunc)
        out += "\n"
        if self.Algorithm == Algo_Table_Driven:
            out += "/**\n"
            out += " * Static table used for the table_driven implementation.\n"
            if self.UndefinedCrcParameters:
                out += " * Must be initialised with the %s function.\n" % (self.PrettyCrcInitFunc)
            out += " *****************************************************************************/\n"
            if self.UndefinedCrcParameters:
                out += "static %s crc_table[%s];\n" % (self.PrettyCrc_t, self.PrettyTableWidth)
            else:
                out += "static const %s crc_table[%s] = %s;\n" % (self.PrettyCrc_t, self.PrettyTableWidth, self.PrettyTableInit)
            out += "\n"
        # crc_reflect
        if self.ReflectIn == None or self.ReflectIn or self.ReflectOut == None or self.ReflectOut:
            out += self.__pretty_crc_reflect_doc()
            out += "long %s(long data, size_t data_len)\n" % (self.PrettyCrcReflectFunc)
            out += "{\n"
            out += "    unsigned int i;\n"
            out += "    long ret;\n"
            out += "\n"
            out += "    ret = 0;\n"
            out += "    for (i = 0; i < data_len; i++)\n"
            out += "    {\n"
            out += "        if (data & 0x01) {\n"
            out += "            ret = (ret << 1) | 1;\n"
            out += "        } else {\n"
            out += "            ret = ret << 1;\n"
            out += "        }\n"
            out += "        data >>= 1;\n"
            out += "    }\n"
            out += "    return ret;\n"
            out += "}\n"
            out += "\n"
        # crc_init
        if not self.ConstantCrcInit:
            out += self.__pretty_crc_init_doc()
            out += "%s %s(const crc_cfg_t *cfg)\n" % (self.PrettyCrc_t, self.PrettyCrcInitFunc)
            out += "{\n"
            if self.Algorithm == Algo_Bit_by_Bit:
                out += "    unsigned int i;\n"
                out += "    bool bit;\n"
                out += "    %s crc = %s;\n" % (self.PrettyCrc_t, self.PrettyXorIn)
                out += "    for (i = 0; i < %s; i++) {\n" % (self.PrettyWidth)
                out += "        bit = crc & 0x01;\n"
                out += "        if (bit) {\n"
                out += "            crc = ((crc ^ %s) >> 1) | %s;\n" % (self.PrettyPoly, self.PrettyMSB_Mask)
                out += "        } else {\n"
                out += "            crc >>= 1;\n"
                out += "        }\n"
                out += "    }\n"
                out += "    return crc & %s;\n" % (self.PrettyMask)
            elif self.Algorithm == Algo_Bit_by_Bit_Fast:
                out += "    return %s & %s;\n" % (self.PrettyXorIn, self.PrettyMask)
            elif self.Algorithm == Algo_Table_Driven:
                if self.ReflectIn == None:
                    out += "    if (%s) {\n" % (self.PrettyReflectIn)
                    out += "        return %s(%s & %s, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyXorIn, self.PrettyMask, self.PrettyWidth)
                    out += "    } else {\n"
                    out += "        return %s & %s;\n" % (self.PrettyXorIn, self.PrettyMask)
                    out += "    }\n"
                elif self.ReflectIn:
                    out += "    return %s(%s & %s, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyXorIn, self.PrettyMask, self.PrettyWidth)
                else:
                    out += "    return %s & %s;\n" % (self.PrettyXorIn, self.PrettyMask)
            out += "}\n"
            out += "\n"
        # crc_update
        if self.Algorithm == Algo_Bit_by_Bit:
            out += self.__pretty_crc_update_doc()
            if self.UndefinedCrcParameters:
                out += "%s %s(const %s *cfg, %s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
            else:
                out += "%s %s(%s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrc_t)
            out += "{\n"
            out += "    unsigned int i;\n"
            out += "    bool bit;\n"
            out += "    unsigned char c;\n"
            out += "\n"
            out += "    while (data_len--) {\n"
            if self.ReflectIn == None:
                out += "        if (%s) {\n" % (self.PrettyReflectIn)
                out += "            c = %s(*data++, 8);\n" % (self.PrettyCrcReflectFunc)
                out += "        } else {\n"
                out += "            c = *data++;\n"
                out += "        }\n"
            elif self.ReflectIn:
                out += "        c = %s(*data++, 8);\n" % (self.PrettyCrcReflectFunc)
            else:
                out += "        c = *data++;\n"
            out += "        for (i = 0; i < 8; i++) {\n"
            out += "            bit = crc & %s;\n" % (self.PrettyMSB_Mask)
            out += "            crc = (crc << 1) | ((c >> (7 - i)) & 0x01);\n"
            out += "            if (bit) {\n"
            out += "                crc ^= %s;\n" % (self.PrettyPoly)
            out += "            }\n"
            out += "        }\n"
            out += "        crc &= %s;\n" % (self.PrettyMask)
            out += "    }\n"
            out += "    return crc & %s;\n" % (self.PrettyMask)
            out += "}\n"
            out += "\n"
            out += "\n"
            # crc_finalize
            out += self.__pretty_crc_finalize_doc()
            if self.UndefinedCrcParameters:
                out += "%s %s(const %s *cfg, %s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
            else:
                out += "%s %s(%s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrc_t)
            out += "{\n"
            out += "    unsigned int i;\n"
            out += "    bool bit;\n"
            out += "\n"
            out += "    for (i = 0; i < %s; i++) {\n" % (self.PrettyWidth)
            out += "        bit = crc & %s;\n" % (self.PrettyMSB_Mask)
            out += "        crc = (crc << 1) | 0x00;\n"
            out += "        if (bit) {\n"
            out += "            crc ^= %s;\n" % (self.PrettyPoly)
            out += "        }\n"
            out += "    }\n"
            if self.ReflectOut == None:
                out += "    if (%s) {\n" % (self.PrettyReflectOut)
                out += "        crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                out += "    }\n"
            elif self.ReflectOut:
                out += "    crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
            out += "    return (crc ^ %s) & %s;\n" % (self.PrettyXorOut, self.PrettyMask)
            out += "}\n"
            out += "\n"
        if self.Algorithm == Algo_Bit_by_Bit_Fast:
            # crc_update
            out += self.__pretty_crc_update_doc()
            if self.UndefinedCrcParameters:
                out += "%s %s(const %s *cfg, %s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
            else:
                out += "%s %s(%s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrc_t)
            out += "{\n"
            out += "    unsigned int i;\n"
            out += "    bool bit;\n"
            out += "    unsigned char c;\n"
            out += "\n"
            out += "    while (data_len--) {\n"
            if self.ReflectIn == None:
                out += "        if (%s) {\n" % (self.PrettyReflectIn)
                out += "            c = %s(*data++, 8);\n" % (self.PrettyCrcReflectFunc)
                out += "        } else {\n"
                out += "            c = *data++;\n"
                out += "        }\n"
            else:
                out += "        c = *data++;\n"
            if self.ReflectIn:
                out += "        for (i = 0x01; i <= 0x80; i <<= 1) {\n"
            else:
                out += "        for (i = 0x80; i > 0; i >>= 1) {\n"
            out += "            bit = crc & %s;\n" % (self.PrettyMSB_Mask)
            out += "            if (c & i) {\n"
            out += "                bit = !bit;\n"
            out += "            }\n"
            out += "            crc <<= 1;\n"
            out += "            if (bit) {\n"
            out += "                crc ^= %s;\n" % (self.PrettyPoly)
            out += "            }\n"
            out += "        }\n"
            out += "        crc &= %s;\n" % (self.PrettyMask)
            out += "    }\n"
            out += "    return crc & %s;\n" % (self.PrettyMask)
            out += "}\n"
            out += "\n"
            out += "\n"
            # crc_finalize
            out += self.__pretty_crc_finalize_doc()
            if not self.InlineFinalizeFunc:
                if self.UndefinedCrcParameters:
                    out += "%s %s(const %s *cfg, %s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
                else:
                    out += "%s %s(crc_t crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrc_t)
                out += "{\n"
                if self.ReflectOut == None:
                    out += "    if (cfg->reflect_out) {\n"
                    out += "        crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                    out += "    }\n"
                elif self.ReflectOut:
                    out += "    crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                out += "    return (crc ^ %s) & %s;\n" % (self.PrettyXorOut, self.PrettyMask)
                out += "}\n"
                out += "\n"
        if self.Algorithm == Algo_Table_Driven:
            # crc_table_gen
            if self.UndefinedCrcParameters:
                out += self.__pretty_crc_table_gen_doc()
                out += "void %s(const %s *cfg)\n" % (self.PrettyCrcGenTableFunc, self.PrettyCrcCfg_t)
                out += "{\n"
                out += "    %s crc;\n" % (self.PrettyCrc_t)
                out += "    unsigned int i, j;\n"
                out += "\n"
                out += "    for (i = 0; i < %s; i++) {\n" % (self.PrettyTableWidth)
                if self.ReflectIn == None:
                    out += "        if (cfg->reflect_in) {\n"
                    out += "            crc = %s(i, %s);\n" % (self.PrettyCrcReflectFunc, self.TableIdxBits)
                    out += "        } else {\n"
                    out += "            crc = i;\n"
                    out += "        }\n"
                elif self.ReflectIn:
                    out += "        crc = %s(i, %s);\n" % (self.PrettyCrcReflectFunc, self.TableIdxBits)
                else:
                    out += "        crc = i;\n"
                out += "        crc <<= (%s - %s);\n" % (self.PrettyWidth, self.TableIdxBits)
                out += "        for (j = 0; j < %s; j++) {\n" % (self.TableIdxBits)
                out += "            if (crc & %s) {\n" % (self.PrettyMSB_Mask)
                out += "                crc = (crc << 1) ^ %s;\n" % (self.PrettyPoly)
                out += "            } else {\n"
                out += "                crc = crc << 1;\n"
                out += "            }\n"
                out += "        }\n"
                if self.ReflectIn == None:
                    out += "        if (cfg->reflect_in) {\n"
                    out += "            crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                    out += "        }\n"
                elif self.ReflectIn:
                    out += "        crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                out += "        crc_table[i] = crc & %s;\n" % (self.PrettyMask)
                out += "    }\n"
                out += "}\n"
                out += "\n"
            # crc_update
            out += self.__pretty_crc_update_doc()
            if self.UndefinedCrcParameters:
                out += "%s %s(const %s *cfg, %s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
            else:
                out += "%s %s(%s crc, const unsigned char *data, size_t data_len)\n" % (self.PrettyCrc_t, self.PrettyCrcUpdateFunc, self.PrettyCrc_t)
            out += "{\n"
            out += "    unsigned int tbl_idx;\n"
            out += "\n"
            if self.ReflectIn == None:
                out += "    if (cfg->reflect_in) {\n"
                out += "        while (data_len--) {\n"
                if self.TableIdxBits == 8:
                    out += "            tbl_idx = (crc ^ *data++) & %s;\n" % (self.PrettyTableMask)
                    out += "            crc = (crc_table[tbl_idx] ^ (crc >> 8)) & %s;\n" % (self.PrettyMask)
                else:
                    for i in range(8 / self.TableIdxBits):
                        out += "            tbl_idx = crc ^ (*data >> %d);\n" % ((i + 0) * self.TableIdxBits)
                        out += "            crc = crc_table[tbl_idx & %s] ^ (crc >> %d);\n" % (self.PrettyTableMask, self.TableIdxBits)
                    out += "            data++;\n"
                out += "        }\n"
                out += "        crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                out += "    } else {\n"
                out += "        while (data_len--) {\n"
                if self.TableIdxBits == 8:
                    out += "            tbl_idx = ((crc >> (%s - 8)) ^ *data++) & %s;\n" % (self.PrettyWidth, self.PrettyTableMask)
                    out += "            crc = (crc_table[tbl_idx] ^ (crc << 8)) & %s;\n" % (self.PrettyMask)
                else:
                    for i in range(8 / self.TableIdxBits):
                        out += "            tbl_idx = (crc >> (%s - %d)) ^ (*data >> %d);\n" % (self.PrettyWidth, self.TableIdxBits, 8 - (i + 1) * self.TableIdxBits)
                        out += "            crc = crc_table[tbl_idx & %s] ^ (crc << %d);\n" % (self.PrettyTableMask, self.TableIdxBits)
                    out += "            data++;\n"
                out += "        }\n"
                out += "    }\n"
            elif self.ReflectIn:
                out += "    while (data_len--) {\n"
                if self.TableIdxBits == 8:
                    out += "        tbl_idx = (crc ^ *data++) & %s;\n" % (self.PrettyTableMask)
                    out += "        crc = crc_table[tbl_idx] ^ (crc >> 8);\n"
                else:
                    for i in range(8 / self.TableIdxBits):
                        out += "        tbl_idx = crc ^ (*data >> %d);\n" % ((i + 0) * self.TableIdxBits)
                        out += "        crc = crc_table[tbl_idx & %s] ^ (crc >> %d);\n" % (self.PrettyTableMask, self.TableIdxBits)
                    out += "        data++;\n"
                out += "    }\n"
                out += "    crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
            else:
                out += "    while (data_len--) {\n"
                if self.TableIdxBits == 8:
                    out += "        tbl_idx = (crc >> (%s - 8)) ^ *data++;\n" % (self.PrettyWidth)
                    out += "        crc = (crc_table[tbl_idx & %s] ^ (crc << 8));\n" % (self.PrettyTableMask)
                else:
                    for i in range(8 / self.TableIdxBits):
                        out += "        tbl_idx = (crc >> %d) ^ (*data >> %d);\n" % (self.Width - self.TableIdxBits, 8 - (i + 1) * self.TableIdxBits)
                        out += "        crc = crc_table[tbl_idx & %s] ^ (crc << %d);\n" % (self.PrettyTableMask, self.TableIdxBits)
                    out += "        data++;\n"
                out += "    }\n"

            out += "    return crc & %s;\n" % (self.PrettyMask)
            out += "}\n"
            if not self.InlineFinalizeFunc:
                out += "\n"
                out += "\n"
                # crc_finalize
                out += self.__pretty_crc_finalize_doc()
                if self.UndefinedCrcParameters:
                    out += "%s %s(const %s *cfg, %s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrcCfg_t, self.PrettyCrc_t)
                else:
                    out += "%s %s(%s crc)\n" % (self.PrettyCrc_t, self.PrettyCrcFinalizeFunc, self.PrettyCrc_t)
                out += "{\n"
                if self.ReflectOut == None:
                    out += "    if (cfg->reflect_out) {\n"
                    out += "        crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                    out += "    }\n"
                elif self.ReflectOut:
                    out += "    crc = %s(crc, %s);\n" % (self.PrettyCrcReflectFunc, self.PrettyWidth)
                out += "    return (crc ^ %s) & %s;\n" % (self.PrettyXorOut, self.PrettyMask)
                out += "}\n"
        return out

    def __generate_c_main(self):
        """
        Return the source code for the main function in a .c file (if desiderated)
        """
        out = self.__generate_c()
        out += "\n"
        out += "\n"
        out += "#include <stdio.h>\n"
        out += "\n"
        out += "/**\n"
        out += " * \\brief      C main function.\n"
        out += " * \\return     0 on success, != 0 on error.\n"
        out += " *****************************************************************************/\n"
        out += "int main(void)\n"
        out += "{\n"
        if self.UndefinedCrcParameters:
            out += "    %s cfg = {\n" % (self.PrettyCrcCfg_t)
            if self.Width == None:
                out += "        0,      // width\n"
            if self.Poly == None:
                out += "        0,      // poly\n"
            if self.XorIn == None:
                out += "        0,      // xor_in\n"
            if self.ReflectIn == None:
                out += "        0,      // reflect_in\n"
            if self.XorOut == None:
                out += "        0,      // xor_out\n"
            if self.ReflectOut == None:
                out += "        0,      // reflect_out\n"
            if self.Width == None:
                out += "\n"
                out += "        0,      // crc_mask\n"
                out += "        0,      // msb_mask\n"
            out += "    };\n"
        out += "    static const unsigned char str[] = \"123456789\";\n"
        out += "    %s crc;\n" % (self.PrettyCrc_t)
        out += "\n"
        if self.UndefinedCrcParameters:
            if self.Algorithm == Algo_Table_Driven:
                out += "    %s(&cfg);\n" % (self.PrettyCrcGenTableFunc)
            out += "    crc = %s(&cfg);\n" % (self.PrettyCrcInitFunc)
            out += "    crc = %s(&cfg, crc, str, sizeof(str) - 1);\n" % (self.PrettyCrcUpdateFunc)
            out += "    crc = %s(&cfg, crc);\n" % (self.PrettyCrcFinalizeFunc)
        else:
            out += "    crc = %s();\n" % (self.PrettyCrcInitFunc)
            out += "    crc = %s(crc, str, sizeof(str) - 1);\n" % (self.PrettyCrcUpdateFunc)
            out += "    crc = %s(crc);\n" % (self.PrettyCrcFinalizeFunc)
        out += "\n"
        out += "    printf(\"0x%lx\\n\", (long)crc);\n"
        out += "    return 0;\n"
        out += "}\n"
        return out

    def generate(self):
        """
        Return the desired source file (.c or .h)
        """
        if self.Action == "generate_h":
            str = self.__generate_h()
        elif self.Action == "generate_c":
            str = self.__generate_c()
        elif self.Action == "generate_c_main":
            str = self.__generate_c_main()
        else:
            str = ""
        return str

def check_string(opt):
    """
    Returns the calculated CRC sum of a string
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    if opt.Algorithm == 0:
        opt.Algorithm = Algo_Bit_by_Bit | Algo_Bit_by_Bit_Fast | Algo_Table_Driven

    crc = this_crc = None
    if opt.Algorithm & Algo_Bit_by_Bit:
        this_crc = crc_bit_by_bit(opt, opt.String)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    if opt.Algorithm & Algo_Bit_by_Bit_Fast:
        this_crc = crc_bit_by_bit_fast(opt, opt.String)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    if opt.Algorithm & Algo_Table_Driven:
        opt.TableIdxBits = 8            # FIXME cowardly refusing to use less bits for the table
        this_crc = crc_table_driven(opt, opt.String)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    return crc


def crc_file_update(opt, tbl, register, str):
    """
    Update the CRC using the table_driven CRC algorithm.
    """
    if not opt.ReflectIn:
        register = opt.XorIn
        for i in range(len(str)):
            octet = ord(str[i])
            tblidx = ((register >> (opt.Width - 8)) ^ octet) & 0xff
            register = ((register << 8) ^ tbl[tblidx]) & opt.Mask
    else:
        register = reflect(opt.XorIn, opt.Width)
        for i in range(len(str)):
            octet = ord(str[i])
            tblidx = (register ^ octet) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & opt.Mask
        register = reflect(register, opt.Width)
    return register

def check_file(opt):
    """
    Calculate the CRC of a file.
    This algorithm uses the table_driven CRC algorithm.
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    tbl = crc_gen_table(opt)

    try:
        file = open(opt.CheckFile, 'rb')
    except:
        sys.stderr.write("Error: can't open file %s\n" % opt.CheckFile)
        sys.exit(1)

    if not opt.ReflectIn:
        register = opt.XorIn
    else:
        register = reflect(opt.XorIn, opt.Width)
    try:
        str = file.read()
    except:
        sys.stderr.write("Error: can't open read %s\n" % opt.CheckFile)
        sys.exit(1)
    while len(str):
        register = crc_file_update(opt, tbl, register, str)
        try:
            str = file.read()
        except:
            sys.stderr.write("Error: can't open read %s\n" % opt.CheckFile)
            sys.exit(1)
    file.close()

    if opt.ReflectOut:
        register = reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register


def main():
    """
    Main function
    """
    opt = Options();
    opt.parse(sys.argv)
    if opt.Verbose:
        renderer = CRenderer(opt)
        print renderer.print_param()
    if opt.Action == "check_string":
        crc = check_string(opt)
        print "0x%x" % crc
    if opt.Action == "check_file":
        crc = check_file(opt)
        print "0x%x" % crc
    if opt.Action == "generate_h" or opt.Action == "generate_c" or opt.Action == "generate_c_main":
        renderer = CRenderer(opt)
        out = renderer.generate()
        if opt.OutputFile == None:
            print out
        else:
            try:
                file = open(opt.OutputFile, "w")
                file.write(out)
                file.close()
            except:
                sys.stderr.write("Error: cannot write to file %s\n" % opt.OutputFile)
                sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
