#  pycrc -- parameterisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2015  Thomas Pircher  <tehpeh-pycrc@tty1.net>
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
Symbol table for the macro processor used by pycrc.
use as follows:

    from crc_opt import Options
    from crc_symtable import SymbolTable

    opt = Options("0.6")
    sym = SymbolTable(opt)

    str = " ....  "
    terminal = sym.get_terminal(str)
"""
#pylint: disable=too-many-lines

from crc_algorithms import Crc
import time
import os


# Class SymbolLookupError
###############################################################################
class SymbolLookupError(Exception):
    """
    The exception class for the symbol table.
    """

    # Class constructor
    ###############################################################################
    def __init__(self, reason):
        Exception.__init__(self)
        self.reason = reason

    # function __str__
    ###############################################################################
    def __str__(self):
        return self.reason


# Class SymbolTable
###############################################################################
class SymbolTable(object):
    """
    The symbol table class.
    """
    # pylint: disable=too-few-public-methods


    # Class constructor
    ###############################################################################
    def __init__(self, opt):
        """
        The class constructor.
        """
        # pylint: disable=line-too-long, too-many-statements

        self.opt = opt

        if self.opt.algorithm == self.opt.algo_table_driven \
                and (self.opt.width == None or self.opt.width < 8):
            if self.opt.width == None:
                self.tbl_shift = None
            else:
                self.tbl_shift = 8 - self.opt.width
        else:
            self.tbl_shift = 0

        self.table = {}
        self.table["nop"] = ""
        self.table["datetime"] = time.asctime()
        self.table["program_version"] = self.opt.version_str
        self.table["program_url"] = self.opt.web_address
        if self.opt.output_file == None:
            self.table["filename"] = "pycrc_stdout"
        else:
            self.table["filename"] = os.path.basename(self.opt.output_file)
        self.table["header_filename"] = self.__pretty_header_filename(self.opt.output_file)

        self.table["crc_width"] = self.__pretty_str(self.opt.width)
        self.table["crc_poly"] = self.__pretty_hex(self.opt.poly, self.opt.width)
        self.table["crc_reflect_in"] = self.__pretty_bool(self.opt.reflect_in)
        self.table["crc_xor_in"] = self.__pretty_hex(self.opt.xor_in, self.opt.width)
        self.table["crc_reflect_out"] = self.__pretty_bool(self.opt.reflect_out)
        self.table["crc_xor_out"] = self.__pretty_hex(self.opt.xor_out, self.opt.width)
        self.table["crc_slice_by"] = str(self.opt.slice_by)
        self.table["crc_table_idx_width"] = str(self.opt.tbl_idx_width)
        self.table["crc_table_width"] = str(1 << self.opt.tbl_idx_width)
        self.table["crc_table_mask"] = self.__pretty_hex(self.opt.tbl_width - 1, 8)
        self.table["crc_mask"] = self.__pretty_hex(self.opt.mask, self.opt.width)
        self.table["crc_msb_mask"] = self.__pretty_hex(self.opt.msb_mask, self.opt.width)
        if self.tbl_shift == None:
            self.table["crc_shift"] = self.__pretty_str(None)
        else:
            self.table["crc_shift"] = self.__pretty_str(self.tbl_shift)

        self.table["cfg_width"] = "$if ($crc_width != Undefined) {:$crc_width:} $else {:cfg->width:}"
        self.table["cfg_poly"] = "$if ($crc_poly != Undefined) {:$crc_poly:} $else {:cfg->poly:}"
        self.table["cfg_poly_shifted"] = "$if ($crc_shift != 0) {:($cfg_poly << $cfg_shift):} $else {:$cfg_poly:}"
        self.table["cfg_reflect_in"] = "$if ($crc_reflect_in != Undefined) {:$crc_reflect_in:} $else {:cfg->reflect_in:}"
        self.table["cfg_xor_in"] = "$if ($crc_xor_in != Undefined) {:$crc_xor_in:} $else {:cfg->xor_in:}"
        self.table["cfg_reflect_out"] = "$if ($crc_reflect_out != Undefined) {:$crc_reflect_out:} $else {:cfg->reflect_out:}"
        self.table["cfg_xor_out"] = "$if ($crc_xor_out != Undefined) {:$crc_xor_out:} $else {:cfg->xor_out:}"
        self.table["cfg_table_idx_width"] = "$if ($crc_table_idx_width != Undefined) {:$crc_table_idx_width:} $else {:cfg->table_idx_width:}"
        self.table["cfg_table_width"] = "$if ($crc_table_width != Undefined) {:$crc_table_width:} $else {:cfg->table_width:}"
        self.table["cfg_mask"] = "$if ($crc_mask != Undefined) {:$crc_mask:} $else {:cfg->crc_mask:}"
        self.table["cfg_mask_shifted"] = "$if ($crc_shift != 0) {:($cfg_mask << $cfg_shift):} $else {:$cfg_mask:}"
        self.table["cfg_msb_mask"] = "$if ($crc_msb_mask != Undefined) {:$crc_msb_mask:} $else {:cfg->msb_mask:}"
        self.table["cfg_msb_mask_shifted"] = "$if ($crc_shift != 0) {:($cfg_msb_mask << $cfg_shift):} $else {:$cfg_msb_mask:}"
        self.table["cfg_shift"] = "$if ($crc_shift != Undefined) {:$crc_shift:} $else {:cfg->crc_shift:}"

        self.table["undefined_parameters"] = self.__pretty_bool(self.opt.undefined_crc_parameters)
        self.table["use_cfg_t"] = self.__pretty_bool(self.opt.undefined_crc_parameters)
        self.table["c_std"] = self.opt.c_std
        self.table["c_bool"] = "$if ($c_std == C89) {:int:} $else {:bool:}"
        self.table["c_true"] = "$if ($c_std == C89) {:1:} $else {:true:}"
        self.table["c_false"] = "$if ($c_std == C89) {:0:} $else {:false:}"

        self.table["underlying_crc_t"] = self.__get_underlying_crc_t()
        self.table["include_files"] = self.__get_include_files()

        self.table["crc_prefix"] = self.opt.symbol_prefix
        self.table["crc_t"] = self.opt.symbol_prefix + "t"
        self.table["cfg_t"] = self.opt.symbol_prefix + "cfg_t"
        self.table["crc_reflect_function"] = self.opt.symbol_prefix + "reflect"
        self.table["crc_table_gen_function"] = self.opt.symbol_prefix + "table_gen"
        self.table["crc_init_function"] = self.opt.symbol_prefix + "init"
        self.table["crc_update_function"] = self.opt.symbol_prefix + "update"
        self.table["crc_finalize_function"] = self.opt.symbol_prefix + "finalize"


    # function get_terminal
    ###############################################################################
    def get_terminal(self, name):
        """
        Return the expanded terminal, if it exists or None otherwise.
        """
        if name != None:
            if name == "":
                return ""
            if name in self.table:
                return self.table[name]
            key = self.__get_terminal(name)
            if key != None:
                self.table[name] = key
                return key
        raise SymbolLookupError('Unknown terminal "{0:s}"'.format(name))


    # function __get_terminal
    ###############################################################################
    def __get_terminal(self, name):
        """
        Return the expanded terminal, if it exists or None otherwise.
        """
        # pylint: disable=line-too-long, too-many-return-statements, too-many-branches, too-many-statements

        if name == "constant_crc_init":
            if self.__get_init_value() == None:
                return  self.__pretty_bool(False)
            else:
                return   self.__pretty_bool(True)

        if name == "constant_crc_table":
            if self.opt.width != None and self.opt.poly != None and self.opt.reflect_in != None:
                return  self.__pretty_bool(True)
            else:
                return   self.__pretty_bool(False)

        elif name == "simple_crc_update_def":
            if self.opt.algorithm in set([self.opt.algo_bit_by_bit, self.opt.algo_bit_by_bit_fast]):
                if self.opt.width != None and self.opt.poly != None and self.opt.reflect_in != None:
                    return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_table_driven:
                if self.opt.width != None and self.opt.reflect_in != None:
                    return  self.__pretty_bool(True)
            return  self.__pretty_bool(False)

        elif name == "inline_crc_finalize":
            if self.opt.algorithm in set([self.opt.algo_bit_by_bit_fast, self.opt.algo_table_driven]) and \
                    (self.opt.width != None and self.opt.reflect_in != None and self.opt.reflect_out != None and self.opt.xor_out != None):
                return  self.__pretty_bool(True)
            else:
                return  self.__pretty_bool(False)

        elif name == "simple_crc_finalize_def":
            if self.opt.algorithm == self.opt.algo_bit_by_bit:
                if self.opt.width != None and self.opt.poly != None and self.opt.reflect_out != None and self.opt.xor_out != None:
                    return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_bit_by_bit_fast:
                if self.opt.width != None and self.opt.reflect_out != None and self.opt.xor_out != None:
                    return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_table_driven:
                if self.opt.width != None and self.opt.reflect_in != None and self.opt.reflect_out != None and self.opt.xor_out != None:
                    return  self.__pretty_bool(True)
            return  self.__pretty_bool(False)

        elif name == "use_reflect_func":
            if self.opt.reflect_out == None or self.opt.reflect_in == None:
                return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_table_driven:
                if self.opt.reflect_in != self.opt.reflect_out:
                    return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_bit_by_bit:
                if self.opt.reflect_in:
                    return  self.__pretty_bool(True)
                if self.opt.reflect_out:
                    return  self.__pretty_bool(True)
            elif self.opt.algorithm == self.opt.algo_bit_by_bit_fast:
                if self.opt.reflect_in:
                    return  self.__pretty_bool(True)
                if self.opt.reflect_out:
                    return  self.__pretty_bool(True)
            return  self.__pretty_bool(False)

        elif name == "static_reflect_func":
            if self.opt.algorithm == self.opt.algo_table_driven:
                return  self.__pretty_bool(False)
            elif self.opt.reflect_out != None and self.opt.algorithm == self.opt.algo_bit_by_bit_fast:
                return  self.__pretty_bool(False)
            else:
                return  self.__pretty_bool(True)

        elif name == "crc_algorithm":
            if self.opt.algorithm == self.opt.algo_bit_by_bit:
                return  "bit-by-bit"
            elif self.opt.algorithm == self.opt.algo_bit_by_bit_fast:
                return  "bit-by-bit-fast"
            elif self.opt.algorithm == self.opt.algo_table_driven:
                return  "table-driven"
            else:
                return  "UNDEFINED"

        elif name == "crc_table_init":
            return  self.__get_table_init()
        elif name == "crc_table_core_algorithm_nonreflected":
            return  self.__get_tbl_core_nonreflected()
        elif name == "crc_table_core_algorithm_reflected":
            return  self.__get_tbl_core_reflected()

        elif name == "header_protection":
            return  self.__pretty_hdrprotection()

        elif name == "crc_init_value":
            ret = self.__get_init_value()
            if ret == None:
                return  ""
            else:
                return  ret

        elif name == "crc_final_value":
            return  """\
$if ($crc_algorithm == "table-driven") {:
$if ($crc_reflect_in == $crc_reflect_out) {:
crc ^ $crc_xor_out\
:} $else {:
$crc_reflect_function(crc, $crc_width) ^ $crc_xor_out\
:}:} $elif ($crc_reflect_out == True) {:
$crc_reflect_function(crc, $crc_width) ^ $crc_xor_out\
:} $else {:
crc ^ $crc_xor_out\
:}"""
        elif name == "h_template":
            return  """\
$source_header
#ifndef $header_protection
#define $header_protection

$if ($include_files != Undefined) {:
$include_files
:}
#include <stdlib.h>
$if ($c_std != C89) {:
#include <stdint.h>
:}
$if ($undefined_parameters == True and $c_std != C89) {:
#include <stdbool.h>
:}

#ifdef __cplusplus
extern "C" {
#endif


/**
 * The definition of the used algorithm.
 *
 * This is not used anywhere in the generated code, but it may be used by the
 * application code to call algoritm-specific code, is desired.
 *****************************************************************************/
$if ($crc_algorithm == "bit-by-bit") {:
#define CRC_ALGO_BIT_BY_BIT 1
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
#define CRC_ALGO_BIT_BY_BIT_FAST 1
:} $elif ($crc_algorithm == "table-driven") {:
#define CRC_ALGO_TABLE_DRIVEN 1
:} $else {:
#define CRC_ALGO_UNKNOWN 1
:}


/**
 * The type of the CRC values.
 *
 * This type must be big enough to contain at least $cfg_width bits.
 *****************************************************************************/
typedef $underlying_crc_t $crc_t;


$if ($undefined_parameters == True) {:
/**
 * The configuration type of the CRC algorithm.
 *****************************************************************************/
typedef struct {
$if ($crc_width == Undefined) {:
    unsigned int width;     /*!< The width of the polynomial */
:}
$if ($crc_poly == Undefined) {:
    $crc_t poly;             /*!< The CRC polynomial */
:}
$if ($crc_reflect_in == Undefined) {:
    $c_bool reflect_in;         /*!< Whether the input shall be reflected or not */
:}
$if ($crc_xor_in == Undefined) {:
    $crc_t xor_in;           /*!< The initial value of the algorithm */
:}
$if ($crc_reflect_out == Undefined) {:
    $c_bool reflect_out;        /*!< Wether the output shall be reflected or not */
:}
$if ($crc_xor_out == Undefined) {:
    $crc_t xor_out;          /*!< The value which shall be XOR-ed to the final CRC value */
:}
$if ($crc_width == Undefined) {:

    /* internal parameters */
    $crc_t msb_mask;             /*!< a bitmask with the Most Significant Bit set to 1
                                     initialise as (crc_t)1u << (width - 1) */
    $crc_t crc_mask;             /*!< a bitmask with all width bits set to 1
                                     initialise as (cfg->msb_mask - 1) | cfg->msb_mask */
    unsigned int crc_shift;     /*!< a shift count that is used when width < 8
                                     initialise as cfg->width < 8 ? 8 - cfg->width : 0 */
:}
} $cfg_t;


:}
$if ($use_reflect_func == True and $static_reflect_func != True) {:
$crc_reflect_doc
$crc_reflect_function_def;


:}
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
$crc_table_gen_doc
$crc_table_gen_function_def;


:}
$crc_init_doc
$if ($constant_crc_init == False) {:
$crc_init_function_def;
:} $elif ($c_std == C89) {:
#define $crc_init_function()      ($crc_init_value)
:} $else {:
static inline $crc_init_function_def$nop
{
    return $crc_init_value;
}
:}


$crc_update_doc
$crc_update_function_def;


$crc_finalize_doc
$if ($inline_crc_finalize == True) {:
$if ($c_std == C89) {:
#define $crc_finalize_function(crc)      ($crc_final_value)
:} $else {:
static inline $crc_finalize_function_def$nop
{
    return $crc_final_value;
}
:}
:} $else {:
$crc_finalize_function_def;
:}


#ifdef __cplusplus
}           /* closing brace for extern "C" */
#endif

#endif      /* $header_protection */
"""

        elif name == "source_header":
            return  """\
/**
 * \\file $filename
 * Functions and types for CRC checks.
 *
 * Generated on $datetime,
 * by $program_version, $program_url
 * using the configuration:
 *    Width         = $crc_width
 *    Poly          = $crc_poly
 *    Xor_In        = $crc_xor_in
 *    ReflectIn     = $crc_reflect_in
 *    Xor_Out       = $crc_xor_out
 *    ReflectOut    = $crc_reflect_out
 *    Algorithm     = $crc_algorithm
$if ($crc_slice_by > 1) {:
 *    SliceBy       = $crc_slice_by
:}
 *****************************************************************************/\
"""

        elif name == "crc_reflect_doc":
            return  """\
/**
 * Reflect all bits of a \\a data word of \\a data_len bytes.
 *
 * \\param data         The data word to be reflected.
 * \\param data_len     The width of \\a data expressed in number of bits.
 * \\return             The reflected data.
 *****************************************************************************/\
"""

        elif name == "crc_reflect_function_def":
            return  """\
$crc_t $crc_reflect_function($crc_t data, size_t data_len)\
"""

        elif name == "crc_reflect_function_gen":
            return  """\
$if ($use_reflect_func == True) {:
$if ($crc_reflect_in == Undefined or $crc_reflect_in == True or $crc_reflect_out == Undefined or $crc_reflect_out == True) {:
$crc_reflect_doc
$crc_reflect_function_def$nop
{
    unsigned int i;
    $crc_t ret;

    ret = data & 0x01;
    for (i = 1; i < data_len; i++) {
        data >>= 1;
        ret = (ret << 1) | (data & 0x01);
    }
    return ret;
}


:}
:}"""

        elif name == "crc_init_function_gen":
            return  """\
$if ($constant_crc_init == False) {:
$crc_init_doc
$crc_init_function_def$nop
{
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;
    $crc_t crc = $cfg_xor_in;
    for (i = 0; i < $cfg_width; i++) {
        bit = crc & 0x01;
        if (bit) {
            crc = ((crc ^ $cfg_poly) >> 1) | $cfg_msb_mask;
        } else {
            crc >>= 1;
        }
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
    return $cfg_xor_in & $cfg_mask;
:} $elif ($crc_algorithm == "table-driven") {:
$if ($crc_reflect_in == Undefined) {:
    if ($cfg_reflect_in) {
        return $crc_reflect_function($cfg_xor_in & $cfg_mask, $cfg_width);
    } else {
        return $cfg_xor_in & $cfg_mask;
    }
:} $elif ($crc_reflect_in == True) {:
    return $crc_reflect_function($cfg_xor_in & $cfg_mask, $cfg_width);
:} $else {:
    return $cfg_xor_in & $cfg_mask;
:}
:}
}


:}"""

        elif name == "crc_update_function_gen":
            return  """\
$crc_table_driven_func_gen
$crc_update_doc
$crc_update_function_def$nop
{
    const unsigned char *d = (const unsigned char *)data;
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;
    unsigned char c;

    while (data_len--) {
$if ($crc_reflect_in == Undefined) {:
        if ($cfg_reflect_in) {
            c = $crc_reflect_function(*d++, 8);
        } else {
            c = *d++;
        }
:} $elif ($crc_reflect_in == True) {:
        c = $crc_reflect_function(*d++, 8);
:} $else {:
        c = *d++;
:}
        for (i = 0; i < 8; i++) {
            bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
            crc = (crc << 1) | ((c >> (7 - i)) & 0x01);
            if (bit) {
                crc ^= $cfg_poly;
            }
        }
        crc &= $cfg_mask;
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
    unsigned int i;
    $c_bool bit;
    unsigned char c;

    while (data_len--) {
$if ($crc_reflect_in == Undefined) {:
        if ($cfg_reflect_in) {
            c = $crc_reflect_function(*d++, 8);
        } else {
            c = *d++;
        }
:} $else {:
        c = *d++;
:}
$if ($crc_reflect_in == True) {:
        for (i = 0x01; i & 0xff; i <<= 1){::}
:} $else {:
        for (i = 0x80; i > 0; i >>= 1){::}
:} {
            bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
            if (c & i) {
                bit = !bit;
            }
            crc <<= 1;
            if (bit) {
                crc ^= $cfg_poly;
            }
        }
        crc &= $cfg_mask;
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "table-driven") {:
    unsigned int tbl_idx;

$if ($crc_reflect_in == Undefined) {:
    if (cfg->reflect_in) {
        while (data_len--) {
$crc_table_core_algorithm_reflected
            d++;
        }
    } else {
        while (data_len--) {
$crc_table_core_algorithm_nonreflected
            d++;
        }
    }
:} $else {:
$if ($crc_slice_by > 1) {:
    const uint32_t *d32 = (const uint32_t *)d;
    while (data_len >= $crc_slice_by)
    {
#if __BYTE_ORDER == __BIG_ENDIAN
        $crc_t d1 = *d32++ ^ le16toh(crc);
$if ($crc_slice_by >= 8) {:
        $crc_t d2 = *d32++;
$if ($crc_slice_by >= 16) {:
        $crc_t d3 = *d32++;
        $crc_t d4 = *d32++;
:}:}
        crc  =
$if ($crc_slice_by == 4) {:
            crc_table[ 0][ d1        & 0xffu] ^
            crc_table[ 1][(d1 >>  8) & 0xffu] ^
            crc_table[ 2][(d1 >> 16) & 0xffu] ^
            crc_table[ 3][(d1 >> 24) & 0xffu];
:} $elif ($crc_slice_by == 8) {:
            crc_table[ 0][ d2        & 0xffu] ^
            crc_table[ 1][(d2 >>  8) & 0xffu] ^
            crc_table[ 2][(d2 >> 16) & 0xffu] ^
            crc_table[ 3][(d2 >> 24) & 0xffu] ^
            crc_table[ 4][ d1        & 0xffu] ^
            crc_table[ 5][(d1 >>  8) & 0xffu] ^
            crc_table[ 6][(d1 >> 16) & 0xffu] ^
            crc_table[ 7][(d1 >> 24) & 0xffu];
:} $elif ($crc_slice_by == 16) {:
            crc_table[ 0][ d4        & 0xffu] ^
            crc_table[ 1][(d4 >>  8) & 0xffu] ^
            crc_table[ 2][(d4 >> 16) & 0xffu] ^
            crc_table[ 3][(d4 >> 24) & 0xffu] ^
            crc_table[ 4][ d3        & 0xffu] ^
            crc_table[ 5][(d3 >>  8) & 0xffu] ^
            crc_table[ 6][(d3 >> 16) & 0xffu] ^
            crc_table[ 7][(d3 >> 24) & 0xffu] ^
            crc_table[ 8][ d2        & 0xffu] ^
            crc_table[ 9][(d2 >>  8) & 0xffu] ^
            crc_table[10][(d2 >> 16) & 0xffu] ^
            crc_table[11][(d2 >> 24) & 0xffu] ^
            crc_table[12][ d1        & 0xffu] ^
            crc_table[13][(d1 >>  8) & 0xffu] ^
            crc_table[14][(d1 >> 16) & 0xffu] ^
            crc_table[15][(d1 >> 24) & 0xffu];
:}
#else
        $crc_t d1 = *d32++ ^ crc;
$if ($crc_slice_by >= 8) {:
        $crc_t d2 = *d32++;
$if ($crc_slice_by >= 16) {:
        $crc_t d3 = *d32++;
        $crc_t d4 = *d32++;
:}:}
        crc  =
$if ($crc_slice_by == 4) {:
            crc_table[ 0][(d1 >> 24) & 0xffu] ^
            crc_table[ 1][(d1 >> 16) & 0xffu] ^
            crc_table[ 2][(d1 >>  8) & 0xffu] ^
            crc_table[ 3][ d1        & 0xffu];
:} $elif ($crc_slice_by == 8) {:
            crc_table[ 0][(d2 >> 24) & 0xffu] ^
            crc_table[ 1][(d2 >> 16) & 0xffu] ^
            crc_table[ 2][(d2 >>  8) & 0xffu] ^
            crc_table[ 3][ d2        & 0xffu] ^
            crc_table[ 4][(d1 >> 24) & 0xffu] ^
            crc_table[ 5][(d1 >> 16) & 0xffu] ^
            crc_table[ 6][(d1 >>  8) & 0xffu] ^
            crc_table[ 7][ d1        & 0xffu];
:} $elif ($crc_slice_by == 16) {:
            crc_table[ 0][(d4 >> 24) & 0xffu] ^
            crc_table[ 1][(d4 >> 16) & 0xffu] ^
            crc_table[ 2][(d4 >>  8) & 0xffu] ^
            crc_table[ 3][ d4        & 0xffu] ^
            crc_table[ 4][(d3 >> 24) & 0xffu] ^
            crc_table[ 5][(d3 >> 16) & 0xffu] ^
            crc_table[ 6][(d3 >>  8) & 0xffu] ^
            crc_table[ 7][ d3        & 0xffu] ^
            crc_table[ 8][(d2 >> 24) & 0xffu] ^
            crc_table[ 9][(d2 >> 16) & 0xffu] ^
            crc_table[10][(d2 >>  8) & 0xffu] ^
            crc_table[11][ d2        & 0xffu] ^
            crc_table[12][(d1 >> 24) & 0xffu] ^
            crc_table[13][(d1 >> 16) & 0xffu] ^
            crc_table[14][(d1 >>  8) & 0xffu] ^
            crc_table[15][ d1        & 0xffu];
:}
#endif

        data_len -= $crc_slice_by;
    }

    /* Remaining bytes with the standard algorithm */
    d = (const unsigned char *)d32;
:}
    while (data_len--) {
$if ($crc_reflect_in == True) {:
$crc_table_core_algorithm_reflected
:} $elif ($crc_reflect_in == False) {:
$crc_table_core_algorithm_nonreflected
:}
        d++;
    }
:}
    return crc & $cfg_mask;
:}
}


"""

        elif name == "crc_finalize_function_gen":
            return  """\
$if ($inline_crc_finalize != True) {:
$crc_finalize_doc
$crc_finalize_function_def$nop
{
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;

    for (i = 0; i < $cfg_width; i++) {
        bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
        crc = (crc << 1) | 0x00;
        if (bit) {
            crc ^= $cfg_poly;
        }
    }
$if ($crc_reflect_out == Undefined) {:
    if ($cfg_reflect_out) {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_out == True) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
$if ($crc_reflect_out == Undefined) {:
    if (cfg->reflect_out) {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_out == True) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:} $elif ($crc_algorithm == "table-driven") {:
$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
$if ($crc_reflect_in == Undefined and $crc_reflect_out == Undefined) {:
    if (cfg->reflect_in == !cfg->reflect_out):}
$elif ($crc_reflect_out == Undefined) {:
    if ($if ($crc_reflect_in == True) {:!:}cfg->reflect_out):}
$elif ($crc_reflect_in == Undefined) {:
    if ($if ($crc_reflect_out == True) {:!:}cfg->reflect_in):} {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_in != $crc_reflect_out) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:}
}


:}"""

        elif name == "crc_table_driven_func_gen":
            return  """\
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
$crc_table_gen_doc
$crc_table_gen_function_def
{
    $crc_t crc;
    unsigned int i, j;

    for (i = 0; i < $cfg_table_width; i++) {
$if ($crc_reflect_in == Undefined) {:
        if (cfg->reflect_in) {
            crc = $crc_reflect_function(i, $cfg_table_idx_width);
        } else {
            crc = i;
        }
:} $elif ($crc_reflect_in == True) {:
        crc = $crc_reflect_function(i, $cfg_table_idx_width);
:} $else {:
        crc = i;
:}
$if ($crc_shift != 0) {:
        crc <<= ($cfg_width - $cfg_table_idx_width + $cfg_shift);
:} $else {:
        crc <<= ($cfg_width - $cfg_table_idx_width);
:}
        for (j = 0; j < $cfg_table_idx_width; j++) {
            if (crc & $cfg_msb_mask_shifted) {
                crc = (crc << 1) ^ $cfg_poly_shifted;
            } else {
                crc = crc << 1;
            }
        }
$if ($crc_reflect_in == Undefined) {:
        if (cfg->reflect_in) {
$if ($crc_shift != 0) {:
            crc = $crc_reflect_function(crc >> $cfg_shift, $cfg_width) << $cfg_shift;
:} $else {:
            crc = $crc_reflect_function(crc, $cfg_width);
:}
        }
:} $elif ($crc_reflect_in == True) {:
$if ($crc_shift != 0) {:
        crc = $crc_reflect_function(crc >> $cfg_shift, $cfg_width) << $cfg_shift;
:} $else {:
        crc = $crc_reflect_function(crc, $cfg_width);
:}
:}
        crc_table[i] = (crc & $cfg_mask_shifted) >> $cfg_shift;
    }
}


:}"""

        elif name == "crc_table_gen_doc":
            return  """\
/**
 * Populate the private static crc table.
 *
 * \\param cfg  A pointer to a initialised $cfg_t structure.
 * \\return     void
 *****************************************************************************/\
"""

        elif name == "crc_table_gen_function_def":
            return  """\
void $crc_table_gen_function(const $cfg_t *cfg)\
"""

        elif name == "crc_init_doc":
            return  """\
/**
 * Calculate the initial crc value.
 *
$if ($use_cfg_t == True) {:
 * \\param cfg  A pointer to a initialised $cfg_t structure.
:}
 * \\return     The initial crc value.
 *****************************************************************************/\
"""

        elif name == "crc_init_function_def":
            return  """\
$if ($constant_crc_init == False) {:
$crc_t $crc_init_function(const $cfg_t *cfg)\
:} $else {:
$crc_t $crc_init_function(void)\
:}\
"""

        elif name == "crc_update_doc":
            return  """\
/**
 * Update the crc value with new data.
 *
 * \\param crc      The current crc value.
$if ($simple_crc_update_def != True) {:
 * \\param cfg      A pointer to a initialised $cfg_t structure.
:}
 * \\param data     Pointer to a buffer of \\a data_len bytes.
 * \\param data_len Number of bytes in the \\a data buffer.
 * \\return         The updated crc value.
 *****************************************************************************/\
"""

        elif name == "crc_update_function_def":
            return  """\
$if ($simple_crc_update_def != True) {:
$crc_t $crc_update_function(const $cfg_t *cfg, $crc_t crc, const void *data, size_t data_len)\
:} $else {:
$crc_t $crc_update_function($crc_t crc, const void *data, size_t data_len)\
:}\
"""

        elif name == "crc_finalize_doc":
            return  """\
/**
 * Calculate the final crc value.
 *
$if ($simple_crc_finalize_def != True) {:
 * \\param cfg  A pointer to a initialised $cfg_t structure.
:}
 * \\param crc  The current crc value.
 * \\return     The final crc value.
 *****************************************************************************/\
"""

        elif name == "crc_finalize_function_def":
            return  """\
$if ($simple_crc_finalize_def != True) {:
$crc_t $crc_finalize_function(const $cfg_t *cfg, $crc_t crc)\
:} $else {:
$crc_t $crc_finalize_function($crc_t crc)\
:}\
"""

        elif name == "c_template":
            return  """\
$source_header
$if ($include_files != Undefined) {:
$include_files
:}
#include "$header_filename"     /* include the header file generated with pycrc */
#include <stdlib.h>
$if ($c_std != C89) {:
#include <stdint.h>
$if ($undefined_parameters == True or $crc_algorithm == "bit-by-bit" or $crc_algorithm == "bit-by-bit-fast") {:
#include <stdbool.h>
:}
:}
$if ($crc_slice_by > 1) {:
#include <endian.h>
:}

$if ($use_reflect_func == True and $static_reflect_func == True) {:
static $crc_reflect_function_def;

:}
$c_table_gen\
$crc_reflect_function_gen\
$crc_init_function_gen\
$crc_update_function_gen\
$crc_finalize_function_gen\
"""

        elif name == "c_table_gen":
            return  """\
$if ($crc_algorithm == "table-driven") {:
/**
 * Static table used for the table_driven implementation.
$if ($undefined_parameters == True) {:
 * Must be initialised with the $crc_init_function function.
:}
 *****************************************************************************/
$if ($constant_crc_table != True) {:
static $crc_t crc_table[$crc_table_width];
:} $else {:
static const $crc_t crc_table$if ($crc_slice_by > 1) {:[$crc_slice_by]:}[$crc_table_width] = $crc_table_init;
:}

:}"""

        elif name == "main_template":
            return  """\
$if ($include_files != Undefined) {:
$include_files
:}
#include <stdio.h>
#include <getopt.h>
$if ($undefined_parameters == True) {:
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
:}
$if ($c_std != C89) {:
#include <stdbool.h>
:}
#include <string.h>

static char str[256] = "123456789";
static $c_bool verbose = $c_false;

void print_params($if ($undefined_parameters == True) {:const $cfg_t *cfg:} $else {:void:});
$getopt_template

void print_params($if ($undefined_parameters == True) {:const $cfg_t *cfg:} $else {:void:})
{
    char format[20];

$if ($c_std == C89) {:
    sprintf(format, "%%-16s = 0x%%0%dlx\\n", (unsigned int)($cfg_width + 3) / 4);
    printf("%-16s = %d\\n", "width", (unsigned int)$cfg_width);
    printf(format, "poly", (unsigned long int)$cfg_poly);
    printf("%-16s = %s\\n", "reflect_in", $if ($crc_reflect_in == Undefined) {:$cfg_reflect_in ? "true": "false":} $else {:$if ($crc_reflect_in == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_in", (unsigned long int)$cfg_xor_in);
    printf("%-16s = %s\\n", "reflect_out", $if ($crc_reflect_out == Undefined) {:$cfg_reflect_out ? "true": "false":} $else {:$if ($crc_reflect_out == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_out", (unsigned long int)$cfg_xor_out);
    printf(format, "crc_mask", (unsigned long int)$cfg_mask);
    printf(format, "msb_mask", (unsigned long int)$cfg_msb_mask);
:} $else {:
    snprintf(format, sizeof(format), "%%-16s = 0x%%0%dllx\\n", (unsigned int)($cfg_width + 3) / 4);
    printf("%-16s = %d\\n", "width", (unsigned int)$cfg_width);
    printf(format, "poly", (unsigned long long int)$cfg_poly);
    printf("%-16s = %s\\n", "reflect_in", $if ($crc_reflect_in == Undefined) {:$cfg_reflect_in ? "true": "false":} $else {:$if ($crc_reflect_in == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_in", (unsigned long long int)$cfg_xor_in);
    printf("%-16s = %s\\n", "reflect_out", $if ($crc_reflect_out == Undefined) {:$cfg_reflect_out ? "true": "false":} $else {:$if ($crc_reflect_out == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_out", (unsigned long long int)$cfg_xor_out);
    printf(format, "crc_mask", (unsigned long long int)$cfg_mask);
    printf(format, "msb_mask", (unsigned long long int)$cfg_msb_mask);
:}
}

/**
 * C main function.
 *
 * \\return     0 on success, != 0 on error.
 *****************************************************************************/
int main(int argc, char *argv[])
{
$if ($undefined_parameters == True) {:
    $cfg_t cfg = {
$if ($crc_width == Undefined) {:
            0,      /* width */
:}
$if ($crc_poly == Undefined) {:
            0,      /* poly */
:}
$if ($crc_xor_in == Undefined) {:
            0,      /* xor_in */
:}
$if ($crc_reflect_in == Undefined) {:
            0,      /* reflect_in */
:}
$if ($crc_xor_out == Undefined) {:
            0,      /* xor_out */
:}
$if ($crc_reflect_out == Undefined) {:
            0,      /* reflect_out */
:}
$if ($crc_width == Undefined) {:

            0,      /* crc_mask */
            0,      /* msb_mask */
            0,      /* crc_shift */
:}
    };
:}
    $crc_t crc;

$if ($undefined_parameters == True) {:
    get_config(argc, argv, &cfg);
:} $else {:
    get_config(argc, argv);
:}
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
    $crc_table_gen_function(&cfg);
:}
    crc = $crc_init_function($if ($constant_crc_init != True) {:&cfg:});
    crc = $crc_update_function($if ($simple_crc_update_def != True) {:&cfg, :}crc, (void *)str, strlen(str));
    crc = $crc_finalize_function($if ($simple_crc_finalize_def != True) {:&cfg, :}crc);

    if (verbose) {
        print_params($if ($undefined_parameters == True) {:&cfg:});
    }
$if ($c_std == C89) {:
    printf("0x%lx\\n", (unsigned long int)crc);
:} $else {:
    printf("0x%llx\\n", (unsigned long long int)crc);
:}
    return 0;
}
"""

        elif name == "getopt_template":
            return  """\
$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
static $c_bool atob(const char *str);
:}
$if ($crc_poly == Undefined or $crc_xor_in == Undefined or $crc_xor_out == Undefined) {:
static crc_t xtoi(const char *str);
:}
static int get_config(int argc, char *argv[]$if ($undefined_parameters == True) {:, $cfg_t *cfg:});


$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
$c_bool atob(const char *str)
{
    if (!str) {
        return 0;
    }
    if (isdigit(str[0])) {
        return ($c_bool)atoi(str);
    }
    if (tolower(str[0]) == 't') {
        return $c_true;
    }
    return $c_false;
}

:}
$if ($crc_poly == Undefined or $crc_xor_in == Undefined or $crc_xor_out == Undefined) {:
crc_t xtoi(const char *str)
{
    crc_t ret = 0;

    if (!str) {
        return 0;
    }
    if (str[0] == '0' && tolower(str[1]) == 'x') {
        str += 2;
        while (*str) {
            if (isdigit(*str))
                ret = 16 * ret + *str - '0';
            else if (isxdigit(*str))
                ret = 16 * ret + tolower(*str) - 'a' + 10;
            else
                return ret;
            str++;
        }
    } else if (isdigit(*str)) {
        while (*str) {
            if (isdigit(*str))
                ret = 10 * ret + *str - '0';
            else
                return ret;
            str++;
        }
    }
    return ret;
}


:}
static int get_config(int argc, char *argv[]$if ($undefined_parameters == True) {:, $cfg_t *cfg:})
{
    int c;
    int option_index;
    static struct option long_options[] = {
$if ($crc_width == Undefined) {:
        {"width",           1, 0, 'w'},
:}
$if ($crc_poly == Undefined) {:
        {"poly",            1, 0, 'p'},
:}
$if ($crc_reflect_in == Undefined) {:
        {"reflect-in",      1, 0, 'n'},
:}
$if ($crc_xor_in == Undefined) {:
        {"xor-in",          1, 0, 'i'},
:}
$if ($crc_reflect_out == Undefined) {:
        {"reflect-out",     1, 0, 'u'},
:}
$if ($crc_xor_out == Undefined) {:
        {"xor-out",         1, 0, 'o'},
:}
        {"verbose",         0, 0, 'v'},
        {"check-string",    1, 0, 's'},
$if ($crc_width == Undefined) {:
        {"table-idx-with",  1, 0, 't'},
:}
        {0, 0, 0, 0}
    };

    while (1) {
        option_index = 0;

        c = getopt_long(argc, argv, "w:p:n:i:u:o:s:vt", long_options, &option_index);
        if (c == -1)
            break;

        switch (c) {
            case 0:
                printf("option %s", long_options[option_index].name);
                if (optarg)
                    printf(" with arg %s", optarg);
                printf("\\n");
$if ($crc_width == Undefined) {:
            case 'w':
                cfg->width = atoi(optarg);
                break;
:}
$if ($crc_poly == Undefined) {:
            case 'p':
                cfg->poly = xtoi(optarg);
                break;
:}
$if ($crc_reflect_in == Undefined) {:
            case 'n':
                cfg->reflect_in = atob(optarg);
                break;
:}
$if ($crc_xor_in == Undefined) {:
            case 'i':
                cfg->xor_in = xtoi(optarg);
                break;
:}
$if ($crc_reflect_out == Undefined) {:
            case 'u':
                cfg->reflect_out = atob(optarg);
                break;
:}
$if ($crc_xor_out == Undefined) {:
            case 'o':
                cfg->xor_out = xtoi(optarg);
                break;
:}
            case 's':
                memcpy(str, optarg, strlen(optarg) < sizeof(str) ? strlen(optarg) + 1 : sizeof(str));
                str[sizeof(str) - 1] = '\\0';
                break;
            case 'v':
                verbose = $c_true;
                break;
$if ($crc_width == Undefined) {:
            case 't':
                /* ignore --table_idx_width option */
                break;
:}
            case '?':
                return -1;
            case ':':
                fprintf(stderr, "missing argument to option %c\\n", c);
                return -1;
            default:
                fprintf(stderr, "unhandled option %c\\n", c);
                return -1;
        }
    }
$if ($crc_width == Undefined) {:
    cfg->msb_mask = (crc_t)1u << (cfg->width - 1);
    cfg->crc_mask = (cfg->msb_mask - 1) | cfg->msb_mask;
    cfg->crc_shift = cfg->width < 8 ? 8 - cfg->width : 0;
:}

$if ($crc_poly == Undefined) {:
    cfg->poly &= $cfg_mask;
:}
$if ($crc_xor_in == Undefined) {:
    cfg->xor_in &= $cfg_mask;
:}
$if ($crc_xor_out == Undefined) {:
    cfg->xor_out &= $cfg_mask;
:}
    return 0;
}\
"""


    # function __pretty_str
    ###############################################################################
    def __pretty_str(self, value):
        """
        Return a value of width bits as a pretty string.
        """
        # pylint: disable=no-self-use

        if value == None:
            return "Undefined"
        return str(value)


    # function __pretty_hex
    ###############################################################################
    def __pretty_hex(self, value, width=None):
        """
        Return a value of width bits as a pretty hexadecimal formatted string.
        """
        # pylint: disable=no-self-use

        if value == None:
            return "Undefined"
        if width == None:
            return "{0:#x}".format(value)
        width = (width + 3) // 4
        hex_str = "{{0:#0{0:d}x}}".format(width + 2)
        return hex_str.format(value)


    # function __pretty_bool
    ###############################################################################
    def __pretty_bool(self, value):
        """
        Return a boolen value of width bits as a pretty formatted string.
        """
        # pylint: disable=no-self-use

        if value == None:
            return "Undefined"
        if value:
            return "True"
        else:
            return "False"


    # function __pretty_header_filename
    ###############################################################################
    def __pretty_header_filename(self, filename):
        """
        Return the sanitized filename of a header file.
        """
        # pylint: disable=no-self-use

        if filename == None:
            return "pycrc_stdout.h"
        filename = os.path.basename(filename)
        if filename[-2:] == ".c":
            return filename[0:-1] + "h"
        else:
            return filename + ".h"


    # function __pretty_hdrprotection
    ###############################################################################
    def __pretty_hdrprotection(self):
        """
        Return the name of a C header protection (e.g. __CRC_IMPLEMENTATION_H__).
        """
        if self.opt.output_file == None:
            filename = "pycrc_stdout"
        else:
            filename = os.path.basename(self.opt.output_file)
        out_str = "".join([s.upper() if s.isalnum() else "_" for s in filename])
        return "__" + out_str + "__"


    # function __get_underlying_crc_t
    ###############################################################################
    def __get_underlying_crc_t(self):
        """
        Return the C type of the crc_t typedef.
        """
        # pylint: disable=too-many-return-statements, too-many-branches

        if self.opt.crc_type != None:
            return self.opt.crc_type
        if self.opt.c_std == "C89":
            if self.opt.width == None:
                return "unsigned long int"
            if self.opt.width <= 8:
                return "unsigned char"
            elif self.opt.width <= 16:
                return "unsigned int"
            else:
                return "unsigned long int"
        else:   # C99
            if self.opt.width == None:
                return "unsigned long long int"
            if self.opt.width <= 8:
                return "uint_fast8_t"
            elif self.opt.width <= 16:
                return "uint_fast16_t"
            elif self.opt.width <= 32:
                return "uint_fast32_t"
            elif self.opt.width <= 64:
                return "uint_fast64_t"
            elif self.opt.width <= 128:
                return "uint_fast128_t"
            else:
                return "uintmax_t"


    # function __get_include_files
    ###############################################################################
    def __get_include_files(self):
        """
        Return an additional include instructions, if specified.
        """
        if self.opt.include_files == None or len(self.opt.include_files) == 0:
            return None
        ret = []
        for include_file in self.opt.include_files:
            if include_file[0] == '"' or include_file[0] == '<':
                ret.append('#include {0}'.format(include_file))
            else:
                ret.append('#include "{0}"'.format(include_file))
        return '\n'.join(ret)


    # function __get_init_value
    ###############################################################################
    def __get_init_value(self):
        """
        Return the init value of a C implementation, according to the selected
        algorithm and to the given options.
        If no default option is given for a given parameter, value in the cfg_t
        structure must be used.
        """
        if self.opt.algorithm == self.opt.algo_bit_by_bit:
            if self.opt.xor_in == None or self.opt.width == None or self.opt.poly == None:
                return None
            crc = Crc(
                width=self.opt.width, poly=self.opt.poly,
                reflect_in=self.opt.reflect_in, xor_in=self.opt.xor_in,
                reflect_out=self.opt.reflect_out, xor_out=self.opt.xor_out,
                table_idx_width=self.opt.tbl_idx_width)
            init = crc.nondirect_init
        elif self.opt.algorithm == self.opt.algo_bit_by_bit_fast:
            if self.opt.xor_in == None:
                return None
            init = self.opt.xor_in
        elif self.opt.algorithm == self.opt.algo_table_driven:
            if self.opt.reflect_in == None or self.opt.xor_in == None or self.opt.width == None:
                return None
            if self.opt.poly == None:
                poly = 0
            else:
                poly = self.opt.poly
            crc = Crc(
                width=self.opt.width, poly=poly,
                reflect_in=self.opt.reflect_in, xor_in=self.opt.xor_in,
                reflect_out=self.opt.reflect_out, xor_out=self.opt.xor_out,
                table_idx_width=self.opt.tbl_idx_width)
            if self.opt.reflect_in:
                init = crc.reflect(crc.direct_init, self.opt.width)
            else:
                init = crc.direct_init
        else:
            init = 0
        return self.__pretty_hex(init, self.opt.width)


    # function __get_simple_table
    ###############################################################################
    def __get_simple_table(self, crc_tbl, values_per_line, format_width, indent):
        """
        Get one CRC table, formatted as string with appropriate indenting and
        line breaks.
        """
        out = ""
        for i in range(self.opt.tbl_width):
            if i % values_per_line == 0:
                out += " " * indent
            tbl_val = self.__pretty_hex(crc_tbl[i], format_width)
            if i == (self.opt.tbl_width - 1):
                out += "{0:s}".format(tbl_val)
            elif i % values_per_line == (values_per_line - 1):
                out += "{0:s},\n".format(tbl_val)
            else:
                out += "{0:s}, ".format(tbl_val)
        return out


    # function __get_table_init
    ###############################################################################
    def __get_table_init(self):
        """
        Return the precalculated CRC table for the table_driven implementation.
        """
        if self.opt.algorithm != self.opt.algo_table_driven:
            return "0"
        if self.opt.width == None or self.opt.poly == None or self.opt.reflect_in == None:
            return "0"
        crc = Crc(
            width=self.opt.width, poly=self.opt.poly,
            reflect_in=self.opt.reflect_in,
            xor_in=0, reflect_out=False, xor_out=0,     # set unimportant variables to known values
            table_idx_width=self.opt.tbl_idx_width,
            slice_by=self.opt.slice_by)
        crc_tbl = crc.gen_table()
        if self.opt.width > 32:
            values_per_line = 4
        elif self.opt.width >= 16:
            values_per_line = 8
        else:
            values_per_line = 16
        format_width = max(self.opt.width, 8)
        if self.opt.slice_by == 1:
            indent = 4
        else:
            indent = 8

        out = [''] * self.opt.slice_by
        for i in range(self.opt.slice_by):
            out[i] = self.__get_simple_table(crc_tbl[i], values_per_line, format_width, indent)
        fixed_indent = ' ' * (indent - 4)
        out = '{0:s}{{\n'.format(fixed_indent) + \
            '\n{0:s}}},\n{0:s}{{\n'.format(fixed_indent).join(out) + \
            '\n{0:s}}}'.format(fixed_indent)
        if self.opt.slice_by == 1:
            return out
        return '{\n' + out + '\n}'


    # function __get_tbl_core_nonreflected
    ###############################################################################
    def __get_tbl_core_nonreflected(self):
        """
        Return the core loop of the table-driven algorithm, non-reflected variant.
        """
        # pylint: disable=too-many-branches

        if self.opt.algorithm != self.opt.algo_table_driven:
            return ""

        loop_core = ""
        loop_indent = ""
        if self.opt.undefined_crc_parameters:
            loop_indent = " " * 12
        else:
            loop_indent = " " * 8

        if self.opt.width == None:
            crc_shifted_right = "(crc >> ($cfg_width - $cfg_table_idx_width))"
        elif self.opt.width < 8:
            shift_val = self.opt.width - self.opt.tbl_idx_width
            if shift_val < 0:
                crc_shifted_right = "(crc << {0})".format(-shift_val)
            else:
                crc_shifted_right = "(crc >> {0})".format(shift_val)
        else:
            shift_val = self.opt.width - self.opt.tbl_idx_width
            if shift_val == 0:
                crc_shifted_right = "crc"
            else:
                crc_shifted_right = "(crc >> {0})".format(shift_val)

        if self.opt.width != None and self.opt.tbl_idx_width != None and \
                self.opt.width <= self.opt.tbl_idx_width:
            crc_xor_expr = ""
        else:
            crc_xor_expr = " ^ (crc << $cfg_table_idx_width)"

        if self.opt.tbl_idx_width == 8:
            if self.opt.slice_by > 1:
                crc_lookup = 'crc_table[0][tbl_idx]'
            else:
                crc_lookup = 'crc_table[tbl_idx]'
            loop_core += loop_indent + "tbl_idx = (" + crc_shifted_right + " ^ *d)" \
                            "$if ($crc_width > 8) {: & $crc_table_mask:};" + '\n' + \
                            loop_indent + "crc = (" + crc_lookup + crc_xor_expr + ") & " + \
                            "$cfg_mask;" + '\n'
        else:
            crc_lookup = 'crc_table[tbl_idx & $crc_table_mask]'
            for i in range(8 // self.opt.tbl_idx_width):
                str_idx = "{0:d}".format(8 - (i + 1) * self.opt.tbl_idx_width)
                loop_core += loop_indent + "tbl_idx = " + crc_shifted_right + \
                             " ^ (*d >> " + str_idx + ");" + '\n' + \
                             loop_indent + "crc = " + crc_lookup + crc_xor_expr + ";" + '\n'
        return loop_core


    # function __get_tbl_core_reflected
    ###############################################################################
    def __get_tbl_core_reflected(self):
        """
        Return the core loop of the table-driven algorithm, reflected variant.
        """
        if self.opt.algorithm != self.opt.algo_table_driven:
            return ""

        loop_core = ""
        loop_indent = ""
        if self.opt.undefined_crc_parameters:
            loop_indent = " " * 12
        else:
            loop_indent = " " * 8
        crc_shifted_right = "crc"
        if self.opt.width != None and self.opt.tbl_idx_width != None and \
                self.opt.width <= self.opt.tbl_idx_width:
            crc_xor_expr = ""
        else:
            crc_xor_expr = " ^ (crc >> $cfg_table_idx_width)"

        if self.opt.tbl_idx_width == 8:
            if self.opt.slice_by > 1:
                crc_lookup = 'crc_table[0][tbl_idx]'
            else:
                crc_lookup = 'crc_table[tbl_idx]'
            loop_core += loop_indent + "tbl_idx = (" + crc_shifted_right + " ^ *d)" \
                            "$if ($crc_width > 8) {: & $crc_table_mask:};" + '\n' + \
                            loop_indent + "crc = (" + crc_lookup + crc_xor_expr + ") & " + \
                            "$cfg_mask;" + '\n'
        else:
            crc_lookup = 'crc_table[tbl_idx & $crc_table_mask]'
            for i in range(8 // self.opt.tbl_idx_width):
                str_idx = "{0:d}".format(i)
                loop_core += loop_indent + "tbl_idx = " + crc_shifted_right + \
                             " ^ (*d >> (" + str_idx + " * $cfg_table_idx_width));" + '\n' + \
                             loop_indent + "crc = " + crc_lookup + crc_xor_expr + ";" + '\n'
        return loop_core
