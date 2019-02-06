#!/usr/bin/env python

#  pycrc -- parameterisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2017  Thomas Pircher  <tehpeh-web@tty1.net>
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
pycrc is a fully parameterisable Cyclic Redundancy Check (CRC) calculation
utility and C source code generator written in Python.

It can:
    -  generate the checksum of a string
    -  generate the checksum of a file
    -  generate the C header file and source of any of the algorithms below

It supports the following CRC algorithms:
    -  bit-by-bit       the basic algorithm which operates bit by bit on the
                        augmented message
    -  bit-by-bit-fast  a variation of the simple bit-by-bit algorithm
    -  table-driven     the standard table driven algorithm
"""

from __future__ import print_function
from pycrc import progname, version, url
from pycrc.opt import Options
from pycrc.algorithms import Crc
import pycrc.codegen as cg
import binascii
import sys



def print_parameters(opt):
    """
    Generate a string with the options pretty-printed (used in the --verbose mode).
    """
    return str(cg.ParamBlock(opt, ''))


def check_string(opt):
    """
    Return the calculated CRC sum of a string.
    """
    error = False
    if opt.undefined_crc_parameters:
        sys.stderr.write("{0:s}: error: undefined parameters\n".format(progname))
        sys.exit(1)
    if opt.algorithm == 0:
        opt.algorithm = opt.algo_bit_by_bit | opt.algo_bit_by_bit_fast | opt.algo_table_driven

    alg = Crc(
        width=opt.width, poly=opt.poly,
        reflect_in=opt.reflect_in, xor_in=opt.xor_in,
        reflect_out=opt.reflect_out, xor_out=opt.xor_out,
        table_idx_width=opt.tbl_idx_width)

    crc = None
    if opt.algorithm & opt.algo_bit_by_bit:
        bbb_crc = alg.bit_by_bit(opt.check_string)
        if crc != None and bbb_crc != crc:
            error = True
        crc = bbb_crc
    if opt.algorithm & opt.algo_bit_by_bit_fast:
        bbf_crc = alg.bit_by_bit_fast(opt.check_string)
        if crc != None and bbf_crc != crc:
            error = True
        crc = bbf_crc
    if opt.algorithm & opt.algo_table_driven:
        # no point making the python implementation slower by using less than 8 bits as index.
        opt.tbl_idx_width = 8
        tbl_crc = alg.table_driven(opt.check_string)
        if crc != None and tbl_crc != crc:
            error = True
        crc = tbl_crc

    if error:
        sys.stderr.write("{0:s}: error: different checksums!\n".format(progname))
        if opt.algorithm & opt.algo_bit_by_bit:
            sys.stderr.write("       bit-by-bit:        {0:#x}\n".format(bbb_crc))
        if opt.algorithm & opt.algo_bit_by_bit_fast:
            sys.stderr.write("       bit-by-bit-fast:   {0:#x}\n".format(bbf_crc))
        if opt.algorithm & opt.algo_table_driven:
            sys.stderr.write("       table_driven:      {0:#x}\n".format(tbl_crc))
        sys.exit(1)
    return crc


def check_hexstring(opt):
    """
    Return the calculated CRC sum of a hex string.
    """
    if opt.undefined_crc_parameters:
        sys.stderr.write("{0:s}: error: undefined parameters\n".format(progname))
        sys.exit(1)
    if len(opt.check_string) % 2 != 0:
        opt.check_string = "0" + opt.check_string
    if sys.version_info >= (3, 0):
        opt.check_string = bytes(opt.check_string, 'utf_8')
    try:
        check_str = bytearray(binascii.unhexlify(opt.check_string))
    except TypeError:
        sys.stderr.write(
            "{0:s}: error: invalid hex string {1:s}\n".format(progname, opt.check_string))
        sys.exit(1)

    opt.check_string = check_str
    return check_string(opt)


def crc_file_update(alg, register, check_bytes):
    """
    Update the CRC using the bit-by-bit-fast CRC algorithm.
    """
    # If the input data is a string, convert to bytes.
    if isinstance(check_bytes, str):
        check_bytes = bytearray(check_bytes, 'utf_8')

    for octet in check_bytes:
        if alg.reflect_in:
            octet = alg.reflect(octet, 8)
        for j in range(8):
            bit = register & alg.msb_mask
            register <<= 1
            if octet & (0x80 >> j):
                bit ^= alg.msb_mask
            if bit:
                register ^= alg.poly
        register &= alg.mask
    return register


def check_file(opt):
    """
    Calculate the CRC of a file.
    This algorithm uses the table_driven CRC algorithm.
    """
    if opt.undefined_crc_parameters:
        sys.stderr.write("{0:s}: error: undefined parameters\n".format(progname))
        sys.exit(1)
    alg = Crc(
        width=opt.width, poly=opt.poly,
        reflect_in=opt.reflect_in, xor_in=opt.xor_in,
        reflect_out=opt.reflect_out, xor_out=opt.xor_out,
        table_idx_width=opt.tbl_idx_width)

    if not opt.reflect_in:
        register = opt.xor_in
    else:
        register = alg.reflect(opt.xor_in, opt.width)

    try:
        with open(opt.check_file, 'rb') as f:
            check_bytes = bytearray(f.read(1024))
            while check_bytes != b"":
                register = crc_file_update(alg, register, check_bytes)
                check_bytes = bytearray(f.read(1024))
    except IOError:
        sys.stderr.write(
            "{0:s}: error: can't open file {1:s}\n".format(progname, opt.check_file))
        sys.exit(1)

    if opt.reflect_out:
        register = alg.reflect(register, opt.width)
    register = register ^ opt.xor_out
    return register


def write_file(filename, out_str):
    """
    Write the content of out_str to filename.
    """
    try:
        out_file = open(filename, "w")
        out_file.write(out_str)
        out_file.close()
    except IOError:
        sys.stderr.write("{0:s}: error: cannot write to file {1:s}\n".format(progname, filename))
        sys.exit(1)


def main():
    """
    Main function.
    """
    opt = Options(progname, version, url)
    opt.parse(sys.argv[1:])
    if opt.verbose:
        print(print_parameters(opt))
    if opt.action == opt.action_check_str:
        crc = check_string(opt)
        print("{0:#x}".format(crc))
    if opt.action == opt.action_check_hex_str:
        crc = check_hexstring(opt)
        print("{0:#x}".format(crc))
    if opt.action == opt.action_check_file:
        crc = check_file(opt)
        print("{0:#x}".format(crc))
    if opt.action in set([
            opt.action_generate_h, opt.action_generate_c, opt.action_generate_c_main,
            opt.action_generate_table]):
        out = str(cg.File(opt, ''))
        if opt.output_file == None:
            print(out)
        else:
            write_file(opt.output_file, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
