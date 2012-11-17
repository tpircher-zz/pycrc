#!/usr/bin/env python

import os
import sys
sys.path.append("..")
from crc_bwe import BitwiseExpression


# main function
###############################################################################
def main():
    """
    Main function
    """
    bwe = BitwiseExpression()

    test_vector = [
        { 'res': "7u", 'exp': "0 | 4 | 2 | (1 | 3)" },
        { 'res': "2u", 'exp': "~(1 | ~3)" },
        { 'res': "4u", 'exp': "2 ^ ~(1 | ~3) ^ 4" },
        { 'res': "1u", 'exp': "0 ^ 1" },
        { 'res': "1u", 'exp': "3 & 1" },
        { 'res': "6u", 'exp': "(1 | 2) << (7 ^ 4 ^ 2)" },
        { 'res': "5u", 'exp': "(8 | 1 | 2) >> (7 ^ 4 ^ 2)" },
        { 'res': "0u", 'exp': "0 & n" },
        { 'res': "n",  'exp': "n & n & ~0 & n" },
        { 'res': "0u", 'exp': "~(~0 | n)" },
        { 'res': "n",  'exp': "n | n | 0 | n" },
        { 'res': "0u", 'exp': "n ^ n" },
        { 'res': "n",  'exp': "~(~0 ^ n)" },
        { 'res': "0u", 'exp': "~(~n ^ n)" },
        { 'res': "7u", 'exp': "1 | x ^ 2 ^ x | 4" },
        { 'res': "0u", 'exp': "x & 0x03 & ~x" },
        { 'res': "1u", 'exp': "~~1 & 0xff" },
        { 'res': "2u", 'exp': "(x | 3 | y) & 0x02" },
        { 'res': "2u", 'exp': "(0xff00 & n | 2) & 0xff" },
        { 'res': "0u", 'exp': "(n & 1) >> 2" },
        { 'res': "0u", 'exp': "(n << 2) & 1" },
        { 'res': "4u", 'exp': "((n & 0xf0 | 1) << 2) & 0x0f" },
        { 'res': "2u", 'exp': "(((0xff00 & n | 2) << 4) & 0xff) >> 4" },
#        { 'res': "?",  'exp': "(((bits << 12) ^ (bits << 13) ^ (bits << 14) ^ (bits << 16) ^ (bits << 17) ^ (bits << 18)) & 262144) | (((bits << 12) ^ (bits << 13) ^ (bits << 14) ^ (bits << 16) ^ (bits << 17) ^ (bits << 18)) & 524288) | (((bits << 12) ^ (bits << 13) ^ (bits << 14) ^ (bits << 16) ^ (bits << 17)) & 131072) | (((bits << 12) ^ (bits << 13) ^ (bits << 14) ^ (bits << 16)) & 65536) | (((bits << 12) ^ (bits << 13) ^ (bits << 8)) & 16384) | (((bits << 12) ^ (bits << 13) ^ (bits << 8)) & 32768) | (((bits << 12) ^ (bits << 13) ^ (bits << 8)) & 8192) | (((bits << 12) ^ (bits << 8)) & 4096) | (((bits << 13) ^ (bits << 14) ^ (bits << 16) ^ (bits << 17)) & 1048576) | (((bits << 14) ^ (bits << 16) ^ (bits << 17) ^ (bits << 19)) & 2097152) | (((bits << 16) ^ (bits << 17) ^ (bits << 19) ^ (bits << 20)) & 4194304) | (((bits << 16) ^ (bits << 17) ^ (bits << 19) ^ (bits << 20)) & 8388608) | (((bits << 17) ^ (bits << 19) ^ (bits << 20) ^ (bits << 22) ^ (bits << 24)) & 16777216) | (((bits << 19) ^ (bits << 20) ^ (bits << 22) ^ (bits << 23) ^ (bits << 24) ^ (bits << 25) ^ (bits << 26)) & 67108864) | (((bits << 19) ^ (bits << 20) ^ (bits << 22) ^ (bits << 23) ^ (bits << 24) ^ (bits << 25)) & 33554432) | (((bits << 1) ^ (bits << 2) ^ (bits << 4) ^ (bits >> 2)) & 16) | (((bits << 1) ^ (bits << 2) ^ (bits << 4) ^ (bits >> 2)) & 32) | (((bits << 1) ^ (bits << 2) ^ (bits << 7)) & 128) | (((bits << 1) ^ (bits << 2) ^ (bits << 7)) & 256) | (((bits << 1) ^ (bits << 2) ^ (bits >> 2)) & 4) | (((bits << 1) ^ (bits << 2) ^ (bits >> 2)) & 8) | (((bits << 1) ^ (bits << 2)) & 64) | (((bits << 1) ^ (bits >> 2)) & 2) | (((bits << 20) ^ (bits << 22) ^ (bits << 23) ^ (bits << 24) ^ (bits << 26)) & 134217728) | (((bits << 22) ^ (bits << 23) ^ (bits << 24) ^ (bits << 28) ^ (bits << 29)) & 536870912) | (((bits << 22) ^ (bits << 23) ^ (bits << 24) ^ (bits << 28)) & 268435456) | (((bits << 23) ^ (bits << 24) ^ (bits << 29) ^ (bits << 30)) & 1073741824) | (((bits << 24) ^ (bits << 30)) & 2147483648) | ((bits << 2) & 512) | ((bits << 8) & 1024) | ((bits << 8) & 2048) | ((bits >> 2) & 1)" },
    ]

    for test in test_vector:
        exp = test['exp']
        chk = test['res']

        print("exp: %s --> %s" % (exp, chk))
        res = bwe.simplify(exp)
        if res != chk:
            print("Error: test failed")
            print("expected:    %s" % chk)
            print("got:         %s" % res)
            return 1

if __name__ == "__main__":
    sys.exit(main())
