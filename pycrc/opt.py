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
Option parsing library for pycrc.
use as follows:

   from pycrc.opt import Options

   opt = Options()
   opt.parse(sys.argv[1:])
"""

from optparse import OptionParser, Option, OptionValueError
from copy import copy
import sys
from pycrc.models import CrcModels


class Options(object):
    """
    The options parsing and validating class.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    # Bitmap of the algorithms
    algo_none = 0x00
    algo_bit_by_bit = 0x01
    algo_bit_by_bit_fast = 0x02
    algo_table_driven = 0x08

    action_check_str = 0x01
    action_check_hex_str = 0x02
    action_check_file = 0x03
    action_generate_h = 0x04
    action_generate_c = 0x05
    action_generate_c_main = 0x06
    action_generate_table = 0x07


    def __init__(self, progname='pycrc', version=None, url=None):
        self.program_name = progname
        self.version = version
        self.version_str = "{0:s} v{1:s}".format(progname, version)
        self.web_address = url

        self.width = None
        self.poly = None
        self.reflect_in = None
        self.xor_in = None
        self.reflect_out = None
        self.xor_out = None
        self.tbl_idx_width = 8
        self.tbl_width = 1 << self.tbl_idx_width
        self.slice_by = 1
        self.verbose = False
        self.check_string = "123456789"
        self.msb_mask = None
        self.mask = None

        self.algorithm = self.algo_none
        self.symbol_prefix = "crc_"
        self.crc_type = None
        self.include_files = []
        self.output_file = None
        self.action = self.action_check_str
        self.check_file = None
        self.c_std = None
        self.undefined_crc_parameters = False


    def parse(self, argv=None):
        """
        Parses and validates the options given as arguments
        """
        # pylint: disable=too-many-branches, too-many-statements

        usage = """python %prog [OPTIONS]

To calculate the checksum of a string or hexadecimal data:
    python %prog [model] --check-string "123456789"
    python %prog [model] --check-hexstring "313233343536373839"

To calculate the checksum of a file:
    python %prog [model] --check-file filename

To generate the C source code and write it to filename:
    python %prog [model] --generate c -o filename

The model can be defined either with the --model switch or by specifying each
of the following parameters:
    --width --poly --reflect-in --xor-in --reflect-out --xor-out"""

        models = CrcModels()
        model_list = ", ".join(models.names())
        parser = OptionParser(option_class=MyOption, usage=usage, version=self.version_str)
        parser.add_option(
                "-v", "--verbose",
                action="store_true", dest="verbose", default=False,
                help="be more verbose; print the value of the parameters "
                "and the chosen model to stdout")
        parser.add_option(
                "--check-string",
                action="store", type="string", dest="check_string",
                help="calculate the checksum of a string (default: '123456789')",
                metavar="STRING")
        parser.add_option(
                "--check-hexstring",
                action="store", type="string", dest="check_hexstring",
                help="calculate the checksum of a hexadecimal number string",
                metavar="STRING")
        parser.add_option(
                "--check-file",
                action="store", type="string", dest="check_file",
                help="calculate the checksum of a file",
                metavar="FILE")
        parser.add_option(
                "--generate",
                action="store", type="string", dest="generate", default=None,
                help="generate C source code; choose the type from {h, c, c-main, table}",
                metavar="CODE")
        parser.add_option(
                "--std",
                action="store", type="string", dest="c_std", default="C99",
                help="choose the C dialect of the generated code from {C89, ANSI, C99}",
                metavar="STD")
        parser.add_option(
                "--algorithm",
                action="store", type="string", dest="algorithm", default="all",
                help="choose an algorithm from "
                "{bit-by-bit, bbb, bit-by-bit-fast, bbf, table-driven, tbl, all}",
                metavar="ALGO")
        parser.add_option(
                "--model",
                action="callback", callback=_model_cb, type="string", dest="model", default=None,
                help="choose a parameter set from {{{0:s}}}".format(model_list),
                metavar="MODEL")
        parser.add_option(
                "--width",
                action="store", type="hex", dest="width",
                help="use NUM bits in the polynomial",
                metavar="NUM")
        parser.add_option(
                "--poly",
                action="store", type="hex", dest="poly",
                help="use HEX as polynomial",
                metavar="HEX")
        parser.add_option(
                "--reflect-in",
                action="store", type="bool", dest="reflect_in",
                help="reflect the octets in the input message",
                metavar="BOOL")
        parser.add_option(
                "--xor-in",
                action="store", type="hex", dest="xor_in",
                help="use HEX as initial value",
                metavar="HEX")
        parser.add_option(
                "--reflect-out",
                action="store", type="bool", dest="reflect_out",
                help="reflect the resulting checksum before applying the --xor-out value",
                metavar="BOOL")
        parser.add_option(
                "--xor-out",
                action="store", type="hex", dest="xor_out",
                help="xor the final CRC value with HEX",
                metavar="HEX")
        parser.add_option(
                "--slice-by",
                action="store", type="int", dest="slice_by",
                help="read NUM bytes at a time from the input. NUM must be one of the values {4, 8, 16}",
                metavar="NUM")
        parser.add_option(
                "--table-idx-width",
                action="store", type="int", dest="table_idx_width",
                help="use NUM bits to index the CRC table; NUM must be one of the values {1, 2, 4, 8}",
                metavar="NUM")
        parser.add_option(
                "--force-poly",
                action="store_true", dest="force_poly", default=False,
                help="override any errors about possibly unsuitable polynoms")
        parser.add_option(
                "--symbol-prefix",
                action="store", type="string", dest="symbol_prefix",
                help="when generating source code, use STRING as prefix to the exported C symbols",
                metavar="STRING")
        parser.add_option(
                "--crc-type",
                action="store", type="string", dest="crc_type",
                help="when generating source code, use STRING as crc_t type",
                metavar="STRING")
        parser.add_option(
                "--include-file",
                action="append", type="string", dest="include_files",
                help="when generating source code, include also FILE as header file; "
                "can be specified multiple times",
                metavar="FILE")
        parser.add_option(
                "-o", "--output",
                action="store", type="string", dest="output_file",
                help="write the generated code to file instead to stdout",
                metavar="FILE")

        (options, args) = parser.parse_args(argv)

        if options.c_std != None:
            std = options.c_std.upper()
            if std == "ANSI" or std == "C89":
                self.c_std = "C89"
            elif std == "C99":
                self.c_std = std
            else:
                self.__error("unknown C standard {0:s}".format(options.c_std))

        undefined_params = []
        if options.width != None:
            self.width = options.width
        else:
            undefined_params.append("--width")
        if options.poly != None:
            self.poly = options.poly
        else:
            undefined_params.append("--poly")
        if options.reflect_in != None:
            self.reflect_in = options.reflect_in
        else:
            undefined_params.append("--reflect-in")
        if options.xor_in != None:
            self.xor_in = options.xor_in
        else:
            undefined_params.append("--xor-in")
        if options.reflect_out != None:
            self.reflect_out = options.reflect_out
        else:
            undefined_params.append("--reflect-out")
        if options.xor_out != None:
            self.xor_out = options.xor_out
        else:
            undefined_params.append("--xor-out")

        if options.table_idx_width != None:
            if options.table_idx_width in set((1, 2, 4, 8)):
                self.tbl_idx_width = options.table_idx_width
                self.tbl_width = 1 << options.table_idx_width
            else:
                self.__error("unsupported table-idx-width {0:d}".format(options.table_idx_width))

        if self.poly != None and self.poly % 2 == 0 and not options.force_poly:
            self.__error("even polinomials are not allowed by default. Use --force-poly to override this.")

        if self.width != None:
            if self.width <= 0:
                self.__error("Width must be strictly positive")
            self.msb_mask = 0x1 << (self.width - 1)
            self.mask = ((self.msb_mask - 1) << 1) | 1
            if self.poly != None and self.poly >> (self.width + 1) != 0 and not options.force_poly:
                self.__error("the polynomial is wider than the supplied Width. Use --force-poly to override this.")
            if self.poly != None:
                self.poly = self.poly & self.mask
            if self.xor_in != None:
                self.xor_in = self.xor_in & self.mask
            if self.xor_out != None:
                self.xor_out = self.xor_out & self.mask
        else:
            self.msb_mask = None
            self.mask = None

        if self.width == None or \
                self.poly == None or \
                self.reflect_in == None or \
                self.xor_in == None or \
                self.reflect_out == None or \
                self.xor_out == None:
            self.undefined_crc_parameters = True
        else:
            self.undefined_crc_parameters = False

        if options.slice_by != None:
            if options.slice_by in set((4, 8, 16)):
                self.slice_by = options.slice_by
            else:
                self.__error("unsupported slice-by {0:d}".format(options.slice_by))
            if self.undefined_crc_parameters:
                self.__error("slice-by is only implemented for fully defined models")
            if self.tbl_idx_width != 8:
                self.__error("slice-by is only implemented for table-idx-width=8")
            # FIXME tp: Fix corner cases and disable the following tests
            if self.width < 8:
                self.__warning("disabling slice-by for width {0}".format(self.width))
                self.slice_by = 1
            if self.width < 16:
                self.__warning("disabling slice-by for width {0}".format(self.width))
                self.slice_by = 1
            if self.width > 32:
                self.__warning("disabling slice-by for width {0}".format(self.width))
                self.slice_by = 1
            if not self.reflect_in:
                self.__warning("disabling slice-by for non-reflected algorithm")
                self.slice_by = 1
# FIXME tp: reintroduce this?
#            if self.width % 8 != 0:
#                self.__error("slice-by is only implemented for width multiples of 8")
#            if options.slice_by < self.width / 8:
#                self.__error("slice-by must be greater or equal width / 8")
            if self.c_std == "C89":
                self.__error("--slice-by not supported for C89")

        if options.algorithm != None:
            alg = options.algorithm.lower()
            if alg in set(["bit-by-bit", "bbb", "all"]):
                self.algorithm |= self.algo_bit_by_bit
            if alg in set(["bit-by-bit-fast", "bbf", "all"]):
                self.algorithm |= self.algo_bit_by_bit_fast
            if alg in set(["table-driven", "tbl", "all"]):
                self.algorithm |= self.algo_table_driven
            if self.algorithm == 0:
                self.__error("unknown algorithm {0:s}".format(options.algorithm))

        if options.symbol_prefix != None:
            self.symbol_prefix = options.symbol_prefix
        if options.include_files != None:
            self.include_files = options.include_files
        if options.crc_type != None:
            self.crc_type = options.crc_type
        if options.output_file != None:
            self.output_file = options.output_file
        op_count = 0
        if options.check_string != None:
            self.action = self.action_check_str
            self.check_string = options.check_string
            op_count += 1
        if options.check_hexstring != None:
            self.action = self.action_check_hex_str
            self.check_string = options.check_hexstring
            op_count += 1
        if options.check_file != None:
            self.action = self.action_check_file
            self.check_file = options.check_file
            op_count += 1
        if options.generate != None:
            arg = options.generate.lower()
            if arg == 'h':
                self.action = self.action_generate_h
            elif arg == 'c':
                self.action = self.action_generate_c
            elif arg == 'c-main':
                self.action = self.action_generate_c_main
            elif arg == 'table':
                self.action = self.action_generate_table
            else:
                self.__error("don't know how to generate {0:s}".format(options.generate))
            op_count += 1

            if self.action == self.action_generate_table:
                if self.algorithm & self.algo_table_driven == 0:
                    self.__error("the --generate table option is incompatible "
                        "with the --algorithm option")
                self.algorithm = self.algo_table_driven
            elif self.algorithm not in set(
                    [self.algo_bit_by_bit, self.algo_bit_by_bit_fast, self.algo_table_driven]):
                self.__error("select an algorithm to be used in the generated file")
        else:
            if self.tbl_idx_width != 8:
                self.__warning("reverting to Table Index Width = 8 "
                    "for internal CRC calculation")
                self.tbl_idx_width = 8
                self.tbl_width = 1 << options.table_idx_width
        if op_count == 0:
            self.action = self.action_check_str
        if op_count > 1:
            self.__error("too many actions specified")

        if len(args) != 0:
            self.__error("unrecognized argument(s): {0:s}".format(" ".join(args)))

        def_params_acts = (self.action_check_str, self.action_check_hex_str,
                           self.action_check_file, self.action_generate_table)
        if self.undefined_crc_parameters and self.action in set(def_params_acts):
            self.__error("undefined parameters: Add {0:s} or use --model"
                .format(", ".join(undefined_params)))
        self.verbose = options.verbose



    def __warning(self, message):
        """
        Print a warning message to stderr.
        """
        sys.stderr.write(
            "{0:s}: warning: {1:s}\n".format(self.program_name, message))



    def __error(self, message):
        """
        Print a error message to stderr and terminate the program.
        """
        sys.stderr.write(
            "{0:s}: error: {1:s}\n".format(self.program_name, message))
        sys.exit(1)


def _model_cb(option, opt_str, value, parser):
    """
    This function sets up the single parameters if the 'model' option has been selected
    by the user.
    """
    model_name = value.lower()
    models = CrcModels()
    model = models.get_params(model_name)
    if model != None:
        setattr(parser.values, 'width', model['width'])
        setattr(parser.values, 'poly', model['poly'])
        setattr(parser.values, 'reflect_in', model['reflect_in'])
        setattr(parser.values, 'xor_in', model['xor_in'])
        setattr(parser.values, 'reflect_out', model['reflect_out'])
        setattr(parser.values, 'xor_out', model['xor_out'])
    else:
        models = CrcModels()
        model_list = ", ".join(models.names())
        raise OptionValueError(
            "unsupported model {0:s}. Supported models are: {1:s}."
            .format(value, model_list))


def _check_hex(dummy_option, opt, value):
    """
    Checks if a value is given in a decimal integer of hexadecimal reppresentation.
    Returns the converted value or rises an exception on error.
    """
    try:
        if value.lower().startswith("0x"):
            return int(value, 16)
        else:
            return int(value)
    except ValueError:
        raise OptionValueError(
            "option {0:s}: invalid integer or hexadecimal value: {1:s}.".format(opt, value))


def _check_bool(dummy_option, opt, value):
    """
    Checks if a value is given as a boolean value (either 0 or 1 or "true" or "false")
    Returns the converted value or rises an exception on error.
    """
    if value.isdigit():
        return int(value, 10) != 0
    elif value.lower() == "false":
        return False
    elif value.lower() == "true":
        return True
    else:
        raise OptionValueError("option {0:s}: invalid boolean value: {1:s}.".format(opt, value))


class MyOption(Option):
    """
    New option parsing class extends the Option class
    """
    TYPES = Option.TYPES + ("hex", "bool")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["hex"] = _check_hex
    TYPE_CHECKER["bool"] = _check_bool

