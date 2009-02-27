#!/usr/bin/env python
# -*- coding: Latin-1 -*-

#  pycrc -- parametrisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2009  Thomas Pircher  <tehpeh@gmx.net>
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
pycrc is a fully parametrisable Cyclic Redundancy Check (CRC) calculation
utility and C source code generator written in Python.

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
import binascii
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
    out += "Direct       = {%crc_direct%}\n"

    mp = MacroParser(opt)
    if not mp.parse(out):
        sys.exit(1)
    return mp.out_str


# function check_string
###############################################################################
def check_string(opt):
    """
    Returns the calculated CRC sum of a string
    """
    error = False
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    if opt.Algorithm == 0:
        opt.Algorithm = opt.Algo_Bit_by_Bit | opt.Algo_Bit_by_Bit_Fast | opt.Algo_Table_Driven

    alg = Crc(width = opt.Width, poly = opt.Poly,
        reflect_in = opt.ReflectIn, xor_in = opt.XorIn,
        reflect_out = opt.ReflectOut, xor_out = opt.XorOut,
        table_idx_width = opt.TableIdxWidth)
    crc = None
    if opt.Algorithm & opt.Algo_Bit_by_Bit:
        bbb_crc = alg.bit_by_bit(opt.CheckString)
        if crc != None and bbb_crc != crc:
            error = True;
        crc = bbb_crc
    if opt.Algorithm & opt.Algo_Bit_by_Bit_Fast:
        bbf_crc = alg.bit_by_bit_fast(opt.CheckString)
        if crc != None and bbf_crc != crc:
            error = True;
        crc = bbf_crc
    if opt.Algorithm & opt.Algo_Table_Driven:
        opt.TableIdxWidth = 8            # FIXME cowardly refusing to use less bits for the table
        tbl_crc = alg.table_driven(opt.CheckString)
        if crc != None and tbl_crc != crc:
            error = True;
        crc - tbl_crc

    if error:
        sys.stderr.write("Error: different checksums:\n");
        if opt.Algorithm & opt.Algo_Bit_by_Bit:
            sys.stderr.write("       bit-by-bit:        0x%x\n" % bbb_crc);
        if opt.Algorithm & opt.Algo_Bit_by_Bit_Fast:
            sys.stderr.write("       bit-by-bit-fast:   0x%x\n" % bbf_crc);
        if opt.Algorithm & opt.Algo_Table_Driven:
            sys.stderr.write("       table_driven:      0x%x\n" % tbl_crc);
        sys.exit(1)
    return crc

# function check_hexstring
###############################################################################
def check_hexstring(opt):
    """
    Returns the calculated CRC sum of a string
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("Error: undefined parameters\n")
        sys.exit(1)
    try:
        str = binascii.unhexlify(opt.CheckString)
    except TypeError:
        sys.stderr.write("Error: invalid hex string %s\n" % opt.CheckString)
        sys.exit(1)

    opt.CheckString = str
    return check_string(opt)

# function crc_file_update
###############################################################################
def crc_file_update(opt, alg, register, str):
    """
    Update the CRC using the bit-by-bit-fast CRC algorithm.
    """
    for i in range(len(str)):
        octet = ord(str[i])
        if alg.ReflectIn:
            octet = alg.reflect(octet, 8)
        for j in range(8):
            bit = register & alg.MSB_Mask
            register <<= 1
            if octet & (0x80 >> j):
                bit ^= alg.MSB_Mask
            if bit:
                register ^= alg.Poly
        register &= alg.Mask    
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
    alg = Crc(width = opt.Width, poly = opt.Poly,
        reflect_in = opt.ReflectIn, xor_in = opt.XorIn,
        reflect_out = opt.ReflectOut, xor_out = opt.XorOut,
        table_idx_width = opt.TableIdxWidth)

    try:
        file = open(opt.CheckFile, 'rb')
    except IOError:
        sys.stderr.write("Error: can't open file %s\n" % opt.CheckFile)
        sys.exit(1)

    if not opt.ReflectIn:
        register = opt.XorIn
    else:
        register = alg.reflect(opt.XorIn, opt.Width)
    try:
        str = file.read()
    except IOError:
        sys.stderr.write("Error: can't open read %s\n" % opt.CheckFile)
        sys.exit(1)
    while len(str):
        register = crc_file_update(opt, alg, register, str)
        try:
            str = file.read()
        except IOError:
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
    opt = Options()
    opt.parse(sys.argv)
    if opt.Verbose:
        print(print_parameters(opt))
    if opt.Action == "check_string":
        crc = check_string(opt)
        print("0x%x" % crc)
    if opt.Action == "check_hexstring":
        crc = check_hexstring(opt)
        print("0x%x" % crc)
    if opt.Action == "check_file":
        crc = check_file(opt)
        print("0x%x" % crc)
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
            print(mp.out_str)
        else:
            try:
                file = open(opt.OutputFile, "w")
                file.write(mp.out_str)
                file.close()
            except IOError:
                sys.stderr.write("Error: cannot write to file %s\n" % opt.OutputFile)
                sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
