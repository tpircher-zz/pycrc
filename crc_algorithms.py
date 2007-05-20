#  pycrc -- flexible CRC calculation utility and C source file generator

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
CRC routines for pycrc.
use as follows:

   from crc_algorithms import Crc

This file is part of pycrc.
"""

# Class Crc
###############################################################################
class Crc(object):
    """
    A bas class for CRC routines.
    """

    # constructor
    ###############################################################################
    def __init__(self, opt):
        self.opt = opt

    # function reflect
    ###############################################################################
    def reflect(self, data, width):
        """
        reflects a data word, i.e. reverts the bit order
        """
        x = 0
        for i in range(width):
            x = x | (((data >> (width - i -1)) & 1) << i)
        return x

    # function handle_bit
    ###############################################################################
    def __handle_bit(self, register, new_bit):
        """
        This function is part of the bit_by_bit algorithm.
        This function takes one bit from the augmented message as argument and returns the new crc value
        """
        register_msb = register & self.opt.MSB_Mask
        register = (register << 1) & self.opt.Mask
        if new_bit != 0:
            register = register | 1
        if register_msb != 0:
            register = register ^ self.opt.Poly
        return register & self.opt.Mask

    # function bit_by_bit
    ###############################################################################
    def bit_by_bit(self, str):
        """
        Classic simple and slow CRC implementation.
        This function iterates bit by bit over the augmented input message and returns the calculated CRC value at the end
        """
        register = self.opt.XorIn
        for j in range(self.opt.Width):
            bit = register & 1
            if bit != 0:
                register = ((register ^ self.opt.Poly) >> 1) | self.opt.MSB_Mask
            else:
                register = register >> 1
        register &= self.opt.Mask

        for i in range(len(str)):
            octet = ord(str[i])
            if self.opt.ReflectIn:
                octet = self.reflect(octet, 8)
            for j in range(8):
                new_bit = octet & (0x80 >> j)
                register = self.__handle_bit(register, new_bit)
        for j in range(self.opt.Width):
            register = self.__handle_bit(register, 0)

        if self.opt.ReflectOut:
            register = self.reflect(register, self.opt.Width)
        register = register ^ self.opt.XorOut
        return register

    # function bit_by_bit_fast
    ###############################################################################
    def bit_by_bit_fast(self, str):
        """
        This is a slightly modified version of the bit_by_bit algorithm: it does not need to loop over the augmented bit,
        i.e. the Width 0-bits wich are appended to the input message in the bit_by_bit algorithm.
        """
        register = self.opt.XorIn

        for i in range(len(str)):
            octet = ord(str[i])
            if self.opt.ReflectIn:
                octet = self.reflect(octet, 8)
            for j in range(8):
                bit = register & self.opt.MSB_Mask
                register <<= 1
                if octet & (0x80 >> j):
                    bit ^= self.opt.MSB_Mask
                if bit:
                    register ^= self.opt.Poly
            register &= self.opt.Mask
        if self.opt.ReflectOut:
            register = self.reflect(register, self.opt.Width)
        register = register ^ self.opt.XorOut
        return register

    # function gen_table
    ###############################################################################
    def gen_table(self):
        """
        This function generates the CRC table used for the table_driven CRC algorithm.
        """
        tbl = {}
        for i in range(1 << self.opt.TableIdxWidth):
            register = i
            if self.opt.ReflectIn:
                register = self.reflect(register, self.opt.TableIdxWidth)
            register = register << (self.opt.Width - self.opt.TableIdxWidth)
            for j in range(self.opt.TableIdxWidth):
                if register & self.opt.MSB_Mask != 0:
                    register = (register << 1) ^ self.opt.Poly
                else:
                    register = (register << 1)
            if self.opt.ReflectIn:
                register = self.reflect(register, self.opt.Width)
            tbl[i] = register & self.opt.Mask
        return tbl

    # function table_driven
    ###############################################################################
    def table_driven(self, str):
        """
        The Standard table_driven CRC algorithm.
        """
        tbl = self.gen_table()

        if not self.opt.ReflectIn:
            register = self.opt.XorIn
            for i in range(len(str)):
                octet = ord(str[i])
                tblidx = ((register >> (self.opt.Width - 8)) ^ octet) & 0xff
                register = ((register << 8) ^ tbl[tblidx]) & self.opt.Mask
        else:
            register = self.reflect(self.opt.XorIn, self.opt.Width)
            for i in range(len(str)):
                octet = ord(str[i])
                tblidx = (register ^ octet) & 0xff
                register = ((register >> 8) ^ tbl[tblidx]) & self.opt.Mask
            register = self.reflect(register, self.opt.Width)

        if self.opt.ReflectOut:
            register = self.reflect(register, self.opt.Width)
        register = register ^ self.opt.XorOut
        return register

