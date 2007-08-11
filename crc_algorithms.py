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
CRC routines for pycrc.
If you want to study the Python implementation of the CRC routines, then you are
in the right place.


Examples
========

This is an example use of the different slgorithms:

>>> from crc_algorithms import Crc
>>> 
>>> class Options(object):
>>>     Width           = 16
>>>     Poly            = 0x8005
>>>     ReflectIn       = True
>>>     XorIn           = 0x0000
>>>     ReflectOut      = True
>>>     XorOut          = 0x0000
>>> 
>>> opt = Options()
>>> crc = Crc(opt)
>>> print "0x%x" % crc.bit_by_bit("123456789")
>>> print "0x%x" % crc.bit_by_bit_fast("123456789")
>>> print "0x%x" % crc.table_driven("123456789")

This file is part of pycrc.
"""

# Class Crc
###############################################################################
class Crc(object):
    """
    A base class for CRC routines.
    """

    # constructor
    ###############################################################################
    def __init__(self, opt):
        """The Crc constructor.

        The opt parameter is an object containing the following members:
            Width
            Poly
            ReflectIn
            XorIn
            ReflectOut
            XorOut
        """
        self.Width          = opt.Width
        self.Poly           = opt.Poly
        self.ReflectIn      = opt.ReflectIn
        self.XorIn          = opt.XorIn
        self.ReflectOut     = opt.ReflectOut
        self.XorOut         = opt.XorOut

        self.MSB_Mask = 0x1 << (opt.Width - 1)
        self.Mask = ((opt.MSB_Mask - 1) << 1) | 1
        try:
            self.TableIdxWidth = opt.TableIdxWidth
            self.TableWidth = 1 << opt.TableIdxWidth
        except:
            self.TableIdxWidth = 8
            self.TableWidth = 1 << self.TableIdxWidth

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
        It function takes one bit from the augmented message as argument and returns the new crc value
        """
        register_msb = register & self.MSB_Mask
        register = (register << 1) & self.Mask
        if new_bit != 0:
            register = register | 1
        if register_msb != 0:
            register = register ^ self.Poly
        return register & self.Mask

    # function bit_by_bit
    ###############################################################################
    def bit_by_bit(self, str):
        """
        Classic simple and slow CRC implementation.
        This function iterates bit by bit over the augmented input message and returns the calculated CRC value at the end
        """
        register = self.XorIn
        for j in range(self.Width):
            bit = register & 1
            if bit != 0:
                register = ((register ^ self.Poly) >> 1) | self.MSB_Mask
            else:
                register = register >> 1
        register &= self.Mask

        for i in range(len(str)):
            octet = ord(str[i])
            if self.ReflectIn:
                octet = self.reflect(octet, 8)
            for j in range(8):
                new_bit = octet & (0x80 >> j)
                register = self.__handle_bit(register, new_bit)
        for j in range(self.Width):
            register = self.__handle_bit(register, 0)

        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        register = register ^ self.XorOut
        return register

    # function bit_by_bit_fast
    ###############################################################################
    def bit_by_bit_fast(self, str):
        """
        This is a slightly modified version of the bit_by_bit algorithm: it does not need to loop over the augmented bit,
        i.e. the Width 0-bits wich are appended to the input message in the bit_by_bit algorithm.
        """
        register = self.XorIn

        for i in range(len(str)):
            octet = ord(str[i])
            if self.ReflectIn:
                octet = self.reflect(octet, 8)
            for j in range(8):
                bit = register & self.MSB_Mask
                register <<= 1
                if octet & (0x80 >> j):
                    bit ^= self.MSB_Mask
                if bit:
                    register ^= self.Poly
            register &= self.Mask
        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        register = register ^ self.XorOut
        return register

    # function gen_table
    ###############################################################################
    def gen_table(self):
        """
        This function generates the CRC table used for the table_driven CRC algorithm.
        The Python version cannot handle tables of a different size rather than 8.
        See the generated C code for tables with different sizes instead.
        """
        tbl = {}
        for i in range(1 << self.TableIdxWidth):
            register = i
            if self.ReflectIn:
                register = self.reflect(register, self.TableIdxWidth)
            register = register << (self.Width - self.TableIdxWidth)
            for j in range(self.TableIdxWidth):
                if register & self.MSB_Mask != 0:
                    register = (register << 1) ^ self.Poly
                else:
                    register = (register << 1)
            if self.ReflectIn:
                register = self.reflect(register, self.Width)
            tbl[i] = register & self.Mask
        return tbl

    # function table_driven
    ###############################################################################
    def table_driven(self, str):
        """
        The Standard table_driven CRC algorithm.
        """
        tbl = self.gen_table()

        if not self.ReflectIn:
            register = self.XorIn
            for i in range(len(str)):
                octet = ord(str[i])
                tblidx = ((register >> (self.Width - 8)) ^ octet) & 0xff
                register = ((register << 8) ^ tbl[tblidx]) & self.Mask
        else:
            register = self.reflect(self.XorIn, self.Width)
            for i in range(len(str)):
                octet = ord(str[i])
                tblidx = (register ^ octet) & 0xff
                register = ((register >> 8) ^ tbl[tblidx]) & self.Mask
            register = self.reflect(register, self.Width)

        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        register = register ^ self.XorOut
        return register

