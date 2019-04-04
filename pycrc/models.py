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
Collection of CRC models. This module contains the CRC models known to pycrc.

To print the parameters of a particular model:

    import pycrc.models as cm

    models = cm.CrcModels()
    print(", ".join(models.names()))
    m = models.get_params("crc-32")
    if m != None:
        print("Width:        {width:d}".format(**m))
        print("Poly:         {poly:#x}".format(**m))
        print("ReflectIn:    {reflect_in}".format(**m))
        print("XorIn:        {xor_in:#x}".format(**m))
        print("ReflectOut:   {reflect_out}".format(**m))
        print("XorOut:       {xor_out:#x}".format(**m))
        print("Check:        {check:#x}".format(**m))
    else:
        print("model not found.")
"""



class CrcModels(object):
    """
    CRC Models.

    All models are defined as constant class variables.
    """

    models = []

    models.append({
        'name':         'crc-3-gsm',
        'width':         3,
        'poly':          0x3,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x7,
        'check':         0x4,
    })
    models.append({
        'name':         'crc-3-rohc',
        'width':         3,
        'poly':          0x3,
        'reflect_in':    True,
        'xor_in':        0x7,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x6,
    })
    models.append({
        'name':         'crc-4-itu',
        'width':         4,
        'poly':          0x3,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x7,
    })
    models.append({
        'name':         'crc-4-interlaken',
        'width':         4,
        'poly':          0x3,
        'reflect_in':    False,
        'xor_in':        0xf,
        'reflect_out':   False,
        'xor_out':       0xf,
        'check':         0xb,
    })
    models.append({
        'name':         'crc-5',
        'width':         5,
        'poly':          0x05,
        'reflect_in':    True,
        'xor_in':        0x1f,
        'reflect_out':   True,
        'xor_out':       0x1f,
        'check':         0x19,
    })
    models.append({
        'name':         'crc-5-epc',
        'width':         5,
        'poly':          0x9,
        'reflect_in':    False,
        'xor_in':        0x9,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x0,
    })
    models.append({
        'name':         'crc-5-itu',
        'width':         5,
        'poly':          0x15,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x07,
    })
    models.append({
        'name':         'crc-6-cdma2000-a',
        'width':         6,
        'poly':          0x27,
        'reflect_in':    False,
        'xor_in':        0x3f,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x0d,
    })
    models.append({
        'name':         'crc-6-cdma2000-b',
        'width':         6,
        'poly':          0x07,
        'reflect_in':    False,
        'xor_in':        0x3f,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x3b,
    })
    models.append({
        'name':         'crc-6-darc',
        'width':         6,
        'poly':          0x19,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x26,
    })
    models.append({
        'name':         'crc-6-itu',
        'width':         6,
        'poly':          0x03,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x06,
    })
    models.append({
        'name':         'crc-6-gsm',
        'width':         6,
        'poly':          0x2f,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x3f,
        'check':         0x13,
    })
    models.append({
        'name':         'crc-7',
        'width':         7,
        'poly':          0x09,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x75,
    })
    models.append({
        'name':         'crc-7-rohc',
        'width':         7,
        'poly':          0x4f,
        'reflect_in':    True,
        'xor_in':        0x7f,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x53,
    })
    models.append({
        'name':         'crc-7-umts',
        'width':         7,
        'poly':          0x45,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x61,
    })
    models.append({
        'name':         'crc-8',
        'width':         8,
        'poly':          0x07,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xf4,
    })
    models.append({
        'name':         'crc-8-autosar',
        'width':         8,
        'poly':          0x2f,
        'reflect_in':    False,
        'xor_in':        0xff,
        'reflect_out':   False,
        'xor_out':       0xff,
        'check':         0xdf,
    })
    models.append({
        'name':         'crc-8-bluetooth',
        'width':         8,
        'poly':          0xa7,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x26,
    })
    models.append({
        'name':         'crc-8-cdma2000',
        'width':         8,
        'poly':          0x9b,
        'reflect_in':    False,
        'xor_in':        0xff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xda,
    })
    models.append({
        'name':         'crc-8-darc',
        'width':         8,
        'poly':          0x39,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x15,
    })
    models.append({
        'name':         'crc-8-dvb-s2',
        'width':         8,
        'poly':          0xd5,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xbc,
    })
    models.append({
        'name':         'crc-8-gsm-a',
        'width':         8,
        'poly':          0x1d,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x37,
    })
    models.append({
        'name':         'crc-8-gsm-b',
        'width':         8,
        'poly':          0x49,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xff,
        'check':         0x94,
    })
    models.append({
        'name':         'crc-8-itu',
        'width':         8,
        'poly':          0x07,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x55,
        'check':         0xa1,
    })
    models.append({
        'name':         'crc-8-i-code',
        'width':         8,
        'poly':          0x1d,
        'reflect_in':    False,
        'xor_in':        0xfd,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x7e,
    })
    models.append({
        'name':         'crc-8-lte',
        'width':         8,
        'poly':          0x9b,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xea,
    })
    models.append({
        'name':         'crc-8-mifare-mad',
        'width':         8,
        'poly':          0x1d,
        'reflect_in':    False,
        'xor_in':        0xc7,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x99,
    })
    models.append({
        'name':         'crc-8-nsrc-5',
        'width':         8,
        'poly':          0x31,
        'reflect_in':    False,
        'xor_in':        0xff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xf7,
    })
    models.append({
        'name':         'crc-8-opensafety',
        'width':         8,
        'poly':          0x2f,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x3e,
    })
    models.append({
        'name':         'crc-8-rohc',
        'width':         8,
        'poly':          0x07,
        'reflect_in':    True,
        'xor_in':        0xff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xd0,
    })
    models.append({
        'name':         'crc-8-sae-j1850',
        'width':         8,
        'poly':          0x1d,
        'reflect_in':    False,
        'xor_in':        0xff,
        'reflect_out':   False,
        'xor_out':       0xff,
        'check':         0x4b,
    })
    models.append({
        'name':         'crc-8-aes',
        'width':         8,
        'poly':          0x1d,
        'reflect_in':    True,
        'xor_in':        0xff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x97,
    })
    models.append({
        'name':         'crc-8-wcdma',
        'width':         8,
        'poly':          0x9b,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x25,
    })
    models.append({
        'name':         'dallas-1-wire',
        'width':         8,
        'poly':          0x31,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xa1,
    })
    models.append({
        'name':         'crc-10',
        'width':         10,
        'poly':          0x233,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x199,
    })
    models.append({
        'name':         'crc-10-cdma2000',
        'width':         10,
        'poly':          0x3d9,
        'reflect_in':    False,
        'xor_in':        0x3ff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x233,
    })
    models.append({
        'name':         'crc-10-gsm',
        'width':         10,
        'poly':          0x175,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x3ff,
        'check':         0x12a,
    })
    models.append({
        'name':         'crc-11',
        'width':         11,
        'poly':          0x385,
        'reflect_in':    False,
        'xor_in':        0x1a,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x5a3,
    })
    models.append({
        'name':         'crc-11-umts',
        'width':         11,
        'poly':          0x307,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x61,
    })
    models.append({
        'name':         'crc-12-cdma2000',
        'width':         12,
        'poly':          0xf13,
        'reflect_in':    False,
        'xor_in':        0xfff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xd4d,
    })
    models.append({
        'name':         'crc-12-dect',
        'width':         12,
        'poly':          0x80f,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xf5b,
    })
    models.append({
        'name':         'crc-12-gsm',
        'width':         12,
        'poly':          0xd31,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xfff,
        'check':         0xb34,
    })
    models.append({
        'name':         'crc-12-3gpp',
        'width':         12,
        'poly':          0x80f,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xdaf,
    })
    models.append({
        'name':         'crc-13-bbc',
        'width':         13,
        'poly':          0x1cf5,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x4fa,
    })
    models.append({
        'name':         'crc-14-darc',
        'width':         14,
        'poly':          0x0805,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x82d,
    })
    models.append({
        'name':         'crc-14-gsm',
        'width':         14,
        'poly':          0x202d,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x3fff,
        'check':         0x30ae,
    })
    models.append({
        'name':         'crc-15',
        'width':         15,
        'poly':          0x4599,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x59e,
    })
    models.append({
        'name':         'crc-15-mpt1327',
        'width':         15,
        'poly':          0x6815,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x1,
        'check':         0x2566,
    })
    models.append({
        'name':         'crc-16',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xbb3d,
    })
    models.append({
        'name':         'crc-16-cdma2000',
        'width':         16,
        'poly':          0xc867,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x4c06,
    })
    models.append({
        'name':         'crc-16-cms',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xaee7,
    })
    models.append({
        'name':         'crc-16-dds-110',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    False,
        'xor_in':        0x800d,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x9ecf,
    })
    models.append({
        'name':         'crc-16-dnp',
        'width':         16,
        'poly':          0x3d65,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0xffff,
        'check':         0xea82,
    })
    models.append({
        'name':         'crc-16-en-13757',
        'width':         16,
        'poly':          0x3d65,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xffff,
        'check':         0xc2b7,
    })
    models.append({
        'name':         'crc-16-gsm',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xffff,
        'check':         0xce3c,
    })
    models.append({
        'name':         'crc-16-lj1200',
        'width':         16,
        'poly':          0x6f63,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xbdf4,
    })
    models.append({
        'name':         'crc-16-maxim',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0xffff,
        'check':         0x44c2,
    })
    models.append({
        'name':         'crc-16-mcrf4xx',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x6f91,
    })
    models.append({
        'name':         'crc-16-nsrc-5',
        'width':         16,
        'poly':          0x080b,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xa066,
    })
    models.append({
        'name':         'crc-16-opensafety-a',
        'width':         16,
        'poly':          0x5935,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x5d38,
    })
    models.append({
        'name':         'crc-16-opensafety-b',
        'width':         16,
        'poly':          0x755b,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x20fe,
    })
    models.append({
        'name':         'crc-16-profibus',
        'width':         16,
        'poly':          0x1dcf,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0xffff,
        'check':         0xa819,
    })
    models.append({
        'name':         'crc-16-riello',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0xb2aa,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x63d0,
    })
    models.append({
        'name':         'crc-16-aug-ccitt',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0x1d0f,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xe5cc,
    })
    models.append({
        'name':         'crc-16-t10-dif',
        'width':         16,
        'poly':          0x8bb7,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xd0db,
    })
    models.append({
        'name':         'crc-16-teledisk',
        'width':         16,
        'poly':          0xa097,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x0fb3,
    })
    models.append({
        'name':         'crc-16-tms37157',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0x89ec,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x26b1,
    })
    models.append({
        'name':         'crc-16-umts',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xfee8,
    })
    models.append({
        'name':         'crc-16-usb',
        'width':         16,
        'poly':          0x8005,
        'reflect_in':    True,
        'xor_in':        0xffff,
        'reflect_out':   True,
        'xor_out':       0xffff,
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
        'check':         0x4b37,
    })
    models.append({
        'name':         'crc-16-genibus',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0xffff,
        'check':         0xd64e,
    })
    models.append({
        'name':         'crc-16-ccitt',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0x1d0f,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xe5cc,
    })
    models.append({
        'name':         'crc-16-ccitt-false',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    False,
        'xor_in':        0xffff,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x29b1,
    })
    models.append({
        'name':         'r-crc-16',
        'width':         16,
        'poly':          0x0589,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x1,
        'check':         0x7e,
    })
    models.append({
        'name':         'x-crc-16',
        'width':         16,
        'poly':          0x0589,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x7f,
    })
    models.append({
        'name':         'crc-a',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0xc6c6,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xbf05,
    })
    models.append({
        'name':         'kermit',
        'width':         16,
        'poly':          0x1021,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
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
        'check':         0x31c3,
    })
    models.append({
        'name':         'crc-17-can-fd',
        'width':         17,
        'poly':          0x1685b,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x4f03,
    })
    models.append({
        'name':         'crc-21-can-fd',
        'width':         21,
        'poly':          0x102899,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xed841,
    })
    models.append({
        'name':         'crc-24',
        'width':         24,
        'poly':          0x864cfb,
        'reflect_in':    False,
        'xor_in':        0xb704ce,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x21cf02,
    })
    models.append({
        'name':         'crc-24-ble',
        'width':         24,
        'poly':          0x65b,
        'reflect_in':    True,
        'xor_in':        0x555555,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xc25a56,
    })
    models.append({
        'name':         'crc-24-flexray-a',
        'width':         24,
        'poly':          0x5d6dcb,
        'reflect_in':    False,
        'xor_in':        0xfedcba,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x7979bd,
    })
    models.append({
        'name':         'crc-24-flexray-b',
        'width':         24,
        'poly':          0x5d6dcb,
        'reflect_in':    False,
        'xor_in':        0xabcdef,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x1f23b8,
    })
    models.append({
        'name':         'crc-24-interlaken',
        'width':         24,
        'poly':          0x328b63,
        'reflect_in':    False,
        'xor_in':        0xffffff,
        'reflect_out':   False,
        'xor_out':       0xffffff,
        'check':         0xb4f3e6,
    })
    models.append({
        'name':         'crc-24-lte-a',
        'width':         24,
        'poly':          0x864cfb,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0xcde703,
    })
    models.append({
        'name':         'crc-24-lte-b',
        'width':         24,
        'poly':          0x800063,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x23ef52,
    })
    models.append({
        'name':         'crc-24-os-9',
        'width':         24,
        'poly':          0x800063,
        'reflect_in':    False,
        'xor_in':        0xffffff,
        'reflect_out':   False,
        'xor_out':       0xffffff,
        'check':         0x200fa5,
    })
    models.append({
        'name':         'crc-30-cdma',
        'width':         30,
        'poly':          0x2030b9c7,
        'reflect_in':    False,
        'xor_in':        0x3fffffff,
        'reflect_out':   False,
        'xor_out':       0x3fffffff,
        'check':         0x4c34abf,
    })
    models.append({
        'name':         'crc-31-philips',
        'width':         31,
        'poly':          0x4c11db7,
        'reflect_in':    False,
        'xor_in':        0x7fffffff,
        'reflect_out':   False,
        'xor_out':       0x7fffffff,
        'check':         0xce9e46c,
    })
    models.append({
        'name':         'crc-32',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
        'check':         0xcbf43926,
    })
    models.append({
        'name':         'crc-32q',
        'width':         32,
        'poly':          0x814141ab,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x3010bf7f,
    })
    models.append({
        'name':         'crc-32-autosar',
        'width':         32,
        'poly':          0xf4acfb13,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
        'check':         0x1697d06a,
    })
    models.append({
        'name':         'crc-32d',
        'width':         32,
        'poly':          0xa833982b,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
        'check':         0x87315576,
    })
    models.append({
        'name':         'crc-32c',
        'width':         32,
        'poly':          0x1edc6f41,
        'reflect_in':    True,
        'xor_in':        0xffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffff,
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
        'check':         0x0376e6e7,
    })
    models.append({
        'name':         'crc-32-bzip2',
        'width':         32,
        'poly':          0x04c11db7,
        'reflect_in':    False,
        'xor_in':        0xffffffff,
        'reflect_out':   False,
        'xor_out':       0xffffffff,
        'check':         0xfc891918,
    })
    models.append({
        'name':         'posix',
        'width':         32,
        'poly':          0x4c11db7,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0xffffffff,
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
        'check':         0xbd0be338,
    })
    models.append({
        'name':         'crc-40-gsm',
        'width':         40,
        'poly':          0x4820009,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0xffffffffff,
        'check':         0xd4164fc646,
    })
    models.append({
        'name':         'crc-64',
        'width':         64,
        'poly':          0x42f0e1eba9ea3693,
        'reflect_in':    False,
        'xor_in':        0x0,
        'reflect_out':   False,
        'xor_out':       0x0,
        'check':         0x6c40df5f0b497347,
    })
    models.append({
        'name':         'crc-64-we',
        'width':         64,
        'poly':          0x42f0e1eba9ea3693,
        'reflect_in':    False,
        'xor_in':        0xffffffffffffffff,
        'reflect_out':   False,
        'xor_out':       0xffffffffffffffff,
        'check':         0x62ec59e3f1a4f00a,
    })
    models.append({
        'name':         'crc-64-go-iso',
        'width':         64,
        'poly':          0x000000000000001b,
        'reflect_in':    True,
        'xor_in':        0xffffffffffffffff,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0xb90956c775a41001,
    })
    models.append({
        'name':         'crc-64-pycrc',
        'width':         64,
        'poly':          0x000000000000001b,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
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
        'check':         0xcaa717168609f281,
    })
    models.append({
        'name':         'crc-64-xz',
        'width':         64,
        'poly':          0x42f0e1eba9ea3693,
        'reflect_in':    True,
        'xor_in':        0xffffffffffffffff,
        'reflect_out':   True,
        'xor_out':       0xffffffffffffffff,
        'check':         0x995dc9bbdf1939fa,
    })
    models.append({
        'name':         'crc-82-darc',
        'width':         82,
        'poly':          0x0308c0111011401440411,
        'reflect_in':    True,
        'xor_in':        0x0,
        'reflect_out':   True,
        'xor_out':       0x0,
        'check':         0x09ea83f625023801fd612,
    })


    def names(self):
        """
        This function returns the list of supported CRC models.
        """
        return [model['name'] for model in self.models]


    def get_params(self, model):
        """
        This function returns the parameters of a given model.
        """
        model = model.lower()
        for i in self.models:
            if i['name'] == model:
                return i
        return None
