# -*- coding: Latin-1 -*-

#  pycrc -- parametrisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2011  Thomas Pircher  <tehpeh@gmx.net>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software",, to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS': WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.


"""
Collection of CRC models[]
use as follows:

   from crc_models import CrcModels

   models = CrcModels()
   print(models.getList())
   m = models.getParams("crc-32")
   if m != None:
       print(m['width'])
       print(m['poly'])
       print(m['reflect_in'])
       print(m['xor_in'])
       print(m['reflect_out'])
       print(m['xor_out'])
       print(m['direct'])
       print(m['check'])

This file is part of pycrc.
"""



# Class CrcModels
###############################################################################
class CrcModels(object):
    """
    CRC Models
    """

    models = []

    models.append({
        'name':         'crc-5',
        'width':         5,
        'poly':          0x05,
        'reflect_in':    True,
        'xor_in':        0x1f,
        'reflect_out':   True,
        'xor_out':       0x1f,
        'direct':        True,
        'check':         0x19,
    })
    models.append({
        'name':         'crc-8',
        'width':         8,
        'poly':          0x07,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0xf4,
    })
    models.append({
        'name':         'dallas-1-wire',
        'width':         8,
        'poly':          0x31,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0xa1,
    })
    models.append({
        'name':         'crc-15',
        'width':         15,
        'poly':          0x4599,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x59e,
    })
    models.append({
        'name':         'crc-16',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0xbb3d,
    })
    models.append({
        'name':         'crc-16-usb',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0xffff,
        'direct':        True,
        'check':         0xb4c8,
    })
    models.append({
        'name':         'crc-16-modbus',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x4b37,
    })
    models.append({
        'name':         'ccitt',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x29b1,
    })
    models.append({
        'name':          'r-crc-16',
        'width':         16,
        'poly':          0x0589,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0001,
        'direct':        True,
        'check':         0x007e,
    })
    models.append({
        'name':         'kermit',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x2189,
    })
    models.append({
        'name':         'x-25',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0xffff,
        'direct':        True,
        'check':         0x906e,
    })
    models.append({
        'name':         'xmodem',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x31c3,
    })
    models.append({
        'name':         'zmodem',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x31c3,
    })
    models.append({
        'name':         'crc-24',
        'width':         24,
        'poly':          0x864cfb,
        'reflect_in':    False,
        'xor_in':        0xb704ce,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x21cf02,
    })
    models.append({
        'name':         'crc-32',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
        'direct':        True,
        'check':         0xcbf43926,
    })
    models.append({
        'name':         'crc-32c',
        'width':         32,
        'poly':          0x1edc6f41,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
        'direct':        True,
        'check':         0xe3069283,
    })
    models.append({
        'name':         'crc-32-mpeg',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    False,
        'xor_in':        0xffffffff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        False,
        'check':         0x0376e6e7,
    })
    models.append({
        'name':         'posix',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xffffffff,
        'direct':        True,
        'check':         0x765e7680,
    })
    models.append({
        'name':         'jam',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x340bc6d9,
    })
    models.append({
        'name':         'xfer',
        'width':         32,
        'poly':          0x000000af,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0xbd0be338,
    })
    models.append({
        'name':         'crc-64',
        'width':         64,
        'poly':          0x000000000000001b,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0x46a5a9388a5beffe,
    })
    models.append({
        'name':         'crc-64-jones',
        'width':         64,
        'poly':          0xad93d23594c935a9,
        'reflect_in':    True,
        'xor_in':        0xffffffffffffffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'direct':        True,
        'check':         0xe9c6d914c4b8d9ca,
    })


    # function getList
    ###############################################################################
    def getList(self):
        """
        This function returns the list of supported CRC models
        """
        l = []
        for i in self.models:
            l.append(i['name'])
        return l


    # function getParams
    ###############################################################################
    def getParams(self, model):
        """
        This function returns the paremeters of a given model
        """
        model = model.lower();
        for i in self.models:
            if i['name'] == model:
                return i
        return None
