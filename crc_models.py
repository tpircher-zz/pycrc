# -*- coding: Latin-1 -*-

#  pycrc -- parametrisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2008  Thomas Pircher  <tehpeh@gmx.net>
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
   print models.getList()
   m = models.getParams("crc-32")
   if m != None:
       print m['width']
       print m['poly']
       print m['reflect_in']
       print m['xor_in']
       print m['reflect_out']
       print m['xor_out']
       print m['check']

This file is part of pycrc.
"""

#import string
#import sys


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
        'poly':          0x05L,
        'reflect_in':    True,
        'xor_in':        0x1fL,
        'reflect_out':   True,
        'xor_out':       0x1fL,
        'check':         0x19L,
    })
    models.append({
        'name':         'crc-8',
        'width':         8,
        'poly':          0x07L,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0xf4L,
    })
    models.append({
        'name':         'dallas-1-wire',
        'width':         8,
        'poly':          0x31L,
        'reflect_in':    True,
        'xor_in':        0x0L,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0xa1L,
    })
    models.append({
        'name':         'crc-15',
        'width':         15,
        'poly':          0x4599L,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0x59eL,
    })
    models.append({
        'name':         'crc-16',
        'width':         16,
        'poly':          0x8005L,
        'reflect_in':    True,
        'xor_in':        0x0L,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0xbb3dL,
    })
    models.append({
        'name':         'crc-16-usb',
        'width':         16,
        'poly':          0x8005L,
        'reflect_in':    True,
        'xor_in':        0xffffL,
        'reflect_out':   True,
        'xor_out':       0xffffL,
        'check':         0xb4c8L,
    })
    models.append({
        'name':         'ccitt',
        'width':         16,
        'poly':          0x1021L,
        'reflect_in':    False,
        'xor_in':        0xffffL,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0x29b1L,
    })
    models.append({
        'name':          'r-crc-16',
        'width':         16,
        'poly':          0x0589L,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0x0001L,
        'check':         0x007eL,
    })
    models.append({
        'name':         'kermit',
        'width':         16,
        'poly':          0x1021L,
        'reflect_in':    True,
        'xor_in':        0x0L,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0x2189L,
    })
    models.append({
        'name':         'x-25',
        'width':         16,
        'poly':          0x1021L,
        'reflect_in':    True,
        'xor_in':        0xffffL,
        'reflect_out':   True,
        'xor_out':       0xffffL,
        'check':         0x906eL,
    })
    models.append({
        'name':         'xmodem',
        'width':         16,
        'poly':          0x8408L,
        'reflect_in':    True,
        'xor_in':        0x0L,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0xc73L,
    })
    models.append({
        'name':         'zmodem',
        'width':         16,
        'poly':          0x1021L,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0x31c3L,
    })
    models.append({
        'name':         'crc-24',
        'width':         24,
        'poly':          0x864cfbL,
        'reflect_in':    False,
        'xor_in':        0xb704ceL,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0x21cf02L,
    })
    models.append({
        'name':         'crc-32',
        'width':         32,
        'poly':          0x4c11db7L,
        'reflect_in':    True,
        'xor_in':        0xffffffffL,
        'reflect_out':   True,
        'xor_out':       0xffffffffL,
        'check':         0xcbf43926L,
    })
    models.append({
        'name':         'crc-32c',
        'width':         32,
        'poly':          0x1edc6f41L,
        'reflect_in':    True,
        'xor_in':        0xffffffffL,
        'reflect_out':   True,
        'xor_out':       0xffffffffL,
        'check':         0xe3069283L,
    })
    models.append({
        'name':         'posix',
        'width':         32,
        'poly':          0x4c11db7L,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0xffffffffL,
        'check':         0x765e7680L,
    })
    models.append({
        'name':         'jam',
        'width':         32,
        'poly':          0x4c11db7L,
        'reflect_in':    True,
        'xor_in':        0xffffffffL,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0x340bc6d9L,
    })
    models.append({
        'name':         'xfer',
        'width':         32,
        'poly':          0x000000afL,
        'reflect_in':    False,
        'xor_in':        0x0L,
        'reflect_out':   False,
        'xor_out':       0x0L,
        'check':         0xbd0be338L,
    })
    models.append({
        'name':         'crc-64',
        'width':         64,
        'poly':          0x000000000000001bL,
        'reflect_in':    True,
        'xor_in':        0x0L,
        'reflect_out':   True,
        'xor_out':       0x0L,
        'check':         0x46a5a9388a5beffeL,
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
