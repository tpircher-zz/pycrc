#!/usr/bin/env python
# -*- coding: Latin-1 -*-

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
pycrc is a flexible CRC calculation utility and C source file generator written in Python.

It can:
    -  generate the checksum of a string
    -  generate the checksum of a file
    -  generate the C header file and source of any of the algorithms below

It supports the following CRC algorithms:
    -  bit-by-bit       the basic algorithm which operates bit by bit on the augmented message
    -  bit-by-bit-fast  a variation of the simple bit-by-bit algorithm
    -  table-driven     the standard table driven algorithm
"""

from crc_opt import Options
from crc_algorithms import Crc
from crc_parser import MacroParser
import sys


# function print_parameters
###############################################################################
def print_parameters(opt):
    """
    Generate a string with the options pretty-printed (used in the --verbose mode)
    """
    out  = ""
    out += "Width        = {%crc_width%}\n"
    out += "Poly         = {%crc_poly%}\n"
    out += "ReflectIn    = {%crc_reflect_in%}\n"
    out += "XorIn        = {%crc_xor_in%}\n"
    out += "ReflectOut   = {%crc_reflect_out%}\n"
    out += "XorOut       = {%crc_xor_out%}\n"
    out += "Algorithm    = {%crc_algorithm%}\n"

    mp = MacroParser(opt)
    if mp.parse(out):
        return mp.out_str
    return ""


# function check_string
###############################################################################
def check_string(opt):
    """
    Returns the calculated CRC sum of a string
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    if opt.Algorithm == 0:
        opt.Algorithm = opt.Algo_Bit_by_Bit | opt.Algo_Bit_by_Bit_Fast | opt.Algo_Table_Driven

    alg = Crc(opt)
    crc = this_crc = None
    if opt.Algorithm & opt.Algo_Bit_by_Bit:
        this_crc = alg.bit_by_bit(opt.CheckString)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    if opt.Algorithm & opt.Algo_Bit_by_Bit_Fast:
        this_crc = alg.bit_by_bit_fast(opt.CheckString)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    if opt.Algorithm & opt.Algo_Table_Driven:
        opt.TableIdxWidth = 8            # FIXME cowardly refusing to use less bits for the table
        this_crc = alg.table_driven(opt.CheckString)
        if crc != None and this_crc != crc:
            sys.stderr.write("Error: different checksums: 0x%x, 0x%x\n" % (this_crc, crc))
            sys.exit(1)
        crc = this_crc
    return crc

# function crc_file_update
###############################################################################
def crc_file_update(opt, alg, tbl, register, str):
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
        register = alg.reflect(opt.XorIn, opt.Width)
        for i in range(len(str)):
            octet = ord(str[i])
            tblidx = (register ^ octet) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & opt.Mask
        register = alg.reflect(register, opt.Width)
    return register

# function check_file
###############################################################################
def check_file(opt):
    """
    Calculate the CRC of a file.
    This algorithm uses the table_driven CRC algorithm.
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    opt.TableIdxWidth = 8            # FIXME cowardly refusing to use less bits for the table

    alg = Crc(opt)
    tbl = alg.gen_table()

    try:
        file = open(opt.CheckFile, 'rb')
    except:
        sys.stderr.write("Error: can't open file %s\n" % opt.CheckFile)
        sys.exit(1)

    if not opt.ReflectIn:
        register = opt.XorIn
    else:
        register = alg.reflect(opt.XorIn, opt.Width)
    try:
        str = file.read()
    except:
        sys.stderr.write("Error: can't open read %s\n" % opt.CheckFile)
        sys.exit(1)
    while len(str):
        register = crc_file_update(opt, alg, tbl, register, str)
        try:
            str = file.read()
        except:
            sys.stderr.write("Error: can't open read %s\n" % opt.CheckFile)
            sys.exit(1)
    file.close()

    if opt.ReflectOut:
        register = alg.reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register

# main function
###############################################################################
def main():
    """
    Main function
    """
    opt = Options("0.6.2");
    opt.parse(sys.argv)
    if opt.Verbose:
        print print_parameters(opt)
    if opt.Action == "check_string":
        crc = check_string(opt)
        print "0x%x" % crc
    if opt.Action == "check_file":
        crc = check_file(opt)
        print "0x%x" % crc
    if opt.Action == "generate_h" or opt.Action == "generate_c" or opt.Action == "generate_c-main" or opt.Action == "generate_table":
        mp = MacroParser(opt)
        if opt.Action == "generate_h":
            in_str = "{%h_template%}"
        elif opt.Action == "generate_c":
            in_str = "{%c_template%}"
        elif opt.Action == "generate_c-main":
            in_str = "{%c_template%}\n\n{%main_template%}"
        elif opt.Action == "generate_table":
            in_str = "{%crc_table_init%}"
        else:
            sys.stderr.write("Error: unknown action %s\n" % opt.Action)
            sys.exit(1)
        if not mp.parse(in_str):
            sys.stderr.write("Error: Failure parsing internal macro language\n")
            sys.exit(1)
        if opt.OutputFile == None:
            print mp.out_str
        else:
            try:
                file = open(opt.OutputFile, "w")
                file.write(mp.out_str)
                file.close()
            except:
                sys.stderr.write("Error: cannot write to file %s\n" % opt.OutputFile)
                sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
