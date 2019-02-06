# Change Log
All notable changes to this project will be documented in this file.
For a detailed list of changes see the [pycrc GitHub][pycrc github] page.
This project adheres to [Semantic Versioning](http://semver.org/).



## [v0.9.2] - 2019-02-06

### Fixed
- Fix code generator to output the table correctly.
  Fixes #28.
- Ensure the data is aligned when using slice-by.
  Fixes #24.


## [v0.9.1] - 2017-09-09

### Added
- Added setup.py script to install pycrc on the system, if desired.
- Added checks about possibly unsuitable polynomials. Use the --force-poly
  option to override the error message.

### Changed
- Completely rewritten the code generator back-end. The new back-end is more
  flexible and allows for a better optimisation of the generated expressions.
- Moved the python code under the `pycrc` directory and changed how the pycrc
  sub-modules are included. Before one would write `import crc_xxx`, now one
  would write `import pycrc.xxx`.
- New license for the documentation:
  [Creative Commons Attribution-Share Alike 4.0 Unported License][CC-BY-SA-4.0].

### Fixed
- Fixed binary files handling with Python 2.7.
  Fixes #11. Thanks to James Bowman.
- Fixed some spelling. Thanks to Frank (ftheile) and ashelly.
- Fixed Header Guard generation. Don't use underscores to start the header
  guard name. Thanks to Andre Hartmann.


## [v0.9] - 2016-01-06

### Added
- Added Stephan Brumme to the `AUTHORS` file as his implementation of the
  slice-by algorithm is the basis for pycrc's implementation.
- Added a new option `--slice-by`. This option is still experimental and
  limited in its use.

### Changed
- Documented the experimental `--slice-by option`.
- Simplified the implementation where Width is less than 8 bits.
- Run the code through `pylint`.
- __API change__: changed the names of the member variables from `CamelCase` to the
  format suggested in `PEP 0008` (lowercase letters and words separated by
  underscore).

### Fixed
- Suppressed the `crc_reflect` function where not needed. Addresses part of #8.
  Thanks to Craig McQueen.
- Allow strings with values greater than 0x80 in `--check-hexstring`.
- When the CRC width is less than 8 then the `bit-by-bit` algorithm needs to
  apply the CRC mask to the final value.
  Fixes #10. Thanks to Steve Geo.
- Fixed the initial value of the 16-bit `CCITT` algorithm. Renamed the model
  from `ccitt` to `crc-16-ccitt`.
  Fixes #7. Thanks to Craig McQueen.


## [v0.8.3] - 2015-08-31

### Changed
- pycrc has a new [homepage][pycrc home].
- The [issue tracker on GitHub][pycrc issues]
  is now advertised as the preferred issue tracker.
- Applied some minor optimisations to the generated table-driven code.
- Belatedly added an authors file. Should I have forgotten to mention someone
  please don't hesitate to send a mail.
- Upgraded documentation to DocBook 5.
- Removed sourceforge mailing list from `README.md` in an effort to move pycrc
  away from sourceforge.
- Removed the experimental `--bitwise-expression` option to facilitate
  restructuring of the code.
- The preferred format for the input data for the Python API is now a byte
  array. But if a string is supplied it is decoded as UTF-8 string.
  Alternative formats are not supported and must be passed to the functions
  as byte arrays.
- Changed the signature of the `crc_update()` function: the data argument is
  now a pointer to void to improve compatibility with C++.
  Thanks to Kamil Szczygieł.
  This closes GitHub issue #4.


## [v0.8.2] - 2014-12-04

### Changed
- Smaller code cleanups.
- Stated more clearly that the bitwise expression algorithm is experimental in
  the documentation.
- Fixed a typo in the documentation.
  The description previously stated:
  "The reflected value of 0xa3 (10100010b) is 0x45 (01000101b)"
  but this should be:
  "The reflected value of 0xa2 (10100010b) is 0x45 (01000101b)"
  Thanks to Andreas Nebenfuehr for reporting the mistake.
- Small cleanups.
  Added a tests for special cases. For now, added `crc-5` with non-inverted
  input. This test is currently failing.
- Removed warning about even polynomials. As Lars Pötter rightly pointed out,
  polynomials may be even.
  Added a caveat emptor about even polinomials in the documentation.

### Fixed
- The table-driven code for polynomials of width < 8 using a table index
  width < 8 was producing a wrong checksum.
  Thanks to Radosław Gancarz.
- Updated the generated code to cope with big Widths (>32 bits) on 32 bit
  processors.
  Since C89 does not give a way to specify the minimum length of a data type,
  the test does not validate C89 code using Widths > 32.
  For C99, the `uint_fastN_t` data types are used or long long, if the Width is
  unknown.


## [v0.8.1] - 2013-05-17

### Changed
- Updated [qm.py from GitHub][qm github].
- Explicitly stated that the output of pycrc is not considered a substantial
  part of the code of pycrc in `README.md`.
- Re-organised the symbol table: grouped the code by functionality, not by
  algorithm.
- The input to the CRC routines can now be bytes or strings.
- Minor formatting change in the manpage.
- Better python3 compatibility.
- Added the files generated with the `bwe` algorithm to `check_files.sh`.

### Fixed
- Fixed a bug in the handling of hexstrings in Python3.
  Thanks to Matthias Kuehlewein.
- Added `--check-hexstring` to the tests.
- Remove obsolete and unused `direct` parameter.
  Merge pull request #2 from smurfix/master.
  Thanks to Matthias Urlichs.
- Don't recurse into main() when an unknown algorithm is selected.
  Merge pull request #2 from smurfix/master.
  Thanks to Matthias Urlichs.


## [v0.8] - 2013-01-04

### Added
- Merged (private) bitwise-expression branch to main.
  This adds the highly experimental `bitwise-expression` (`bwe`) code generator
  target, which might one day be almost as fast as the table-driven code but
  much smaller.
  At the moment the generated code is bigger and slower than any other
  algorithm, so use at your own risk.

### Changed
- Now it is possible to specify the `--include` option multiple times.
- Completely revisited and reworked the documentation.
- Updated the command line help screen with more useful command descriptions.
- Removed the `-*- coding: Latin-1 -*-` string.
- Updated the copyright year to 2013.
- Renamed abbreviations to `bbb`, `bbf`, `tbl`.
- It is possible now to abbreviate the algorithms (`bbb` for `bit-by-bit`,
  `bbf` for `bit-by-bit-fast` and `tbl` for `table-driven`).
  Added the list of supported CRC models to the error message when an
  unknown model parameter was supplied.
- Documented the possibility to abbreviate the algorithms. Minor
  improvements in the documentation.
- Added a note to `README.md` that version 0.7.10 of pycrc is the last one
  known to work with Python 2.4.
- Updated a link to the list of CRC models.
- Renamed i`README` to `README.md`.
- Updated link to the [Catalogue of parametrised CRC algorithms][crc catalogue].


## [v0.7.11] - 2012-10-20

### Changed
- Improved Python3 compatibility. pycrc now requires Python 2.6 or later.
- Added a test for compiled standard models.

### Fixed
- Fixed a wrong `check` value of the `crc-64-jones` model.
- Don't use `snprintf()` with `c89` code, changed to `sprintf()`.
- Deleted `test.sh` shell script and replaced it with `test.py`.


## [v0.7.10] - 2012-02-13

### Added
- Added the models `crc-12-3gpp`, `crc-16-genibus`, `crc-32-bzip2` and `crc-64-xz`.
  Taken from [Greg Cook's Catalogue of parametrised CRC algorithms][crc catalogue].

### Changed
- Bad-looking C code generated; make sure the `bit-by-bit`(`-fast`) code does not
  contain two instructions on one line. Thanks to "intgr" for the fix.
- Some small code clean-up: use `set()` when appropriate.

### Fixed
- Fixed a mistake in the man page that still used the old model name
  `crc-32mpeg` instead of `crc-32-mpeg`.  Thanks to Marek Erban.


## [v0.7.9] - 2011-12-08

### Fixed
- Fixed a bug in the generated C89 code that included `stdint.h`.
  Thanks to Frank (ftheile).
  Closes issue 3454356.
- Fixed a bug in the generated C89 code when using a 64 bit CRC.
- Using the `--verbose` option made pycrc quit without error message.


## [v0.7.8] - 2011-07-10

### Changed
- When generating C code for the C89 or ANSI standard, don't include `stdint.h`.
  This closes issue 3338930
- If no output file name is given while generating a C file, then pycrc will
  `#include` a hypothetical `pycrc.h` file instead of a `stdout.h` file.
  Also, added a comment on that line to make debugging easier.
  Closes issue 3325109.
- Removed unused variable `this_option_optind` in the generated option parser.


## [v0.7.7] - 2011-02-11

### Changed
- Updated the copyright year.
  Fixed some coding style issues found by `pylint` and `pychecker`.

### Fixed
- Substituted the deprecated function `atoi()` with `int()`. Closes issue 3136566.
  Thanks to Tony Smith.
- Updated the documentation using Windows-style calls to the Python interpreter.


## [v0.7.6] - 2010-10-21

### Changed
- Rewritten macro parser from scratch. Simplified the macro language.
- Changed a simple division (/) to a integer division (//) for Python3
  compatibility.

### Fixed
- Fixed a minor bug in the command line parsing of the generated main function.


## [v0.7.5] - 2010-03-28

### Added
- Python implementation of the `table-driven` algorithm can handle widths less
  than 8.
- Suppressed warnings of unused cfg structure on partially defined models.

### Removed
- Removed the half-baken and confusing `--direct` option.

### Changed
- C/C++ code can now be generated for the table-driven algorithm with widths
  that are not byte-aligned or less than 8.
  This feature was heavily inspired by a similar feature in Danjel McGougan's
  [Universal Crc][universal crc].
- __API change__: introduced new variable `crc_shift`, member of the `crc_cfg_t`
  structure, which must be initialised manually when the width was undefined
  during C/C++ code generation.
- Minor code cleanup.


## [v0.7.4] - 2010-01-24

### Added
- Added `crc-16-modbus`. Closes issue 2896611.

### Changed
- Changed the `xor-in` value of the `crc-64-jones` model.
- Set xmodem parameters equal to the `zmodem` parameters.
- Generate more uniform error messages.
- Added a warning for even polynomials.

### Fixed
- Fix for unused variable argv.
  Closes issue 2893224. Thanks to Marko von Oppen.


## [v0.7.3] - 2009-10-25

### Added
- Added `crc-64-jones` CRC model. Thanks to Waterspirit.

### Changed
- Renamed `crc-32mpeg` to `crc-32-mpeg`.


## [v0.7.2] - 2009-09-30

### Fixed
- Fixed a bug that caused the result of the Python `table-driven` code not
  being evaluated at all.
  Closes issue 2870630. Thanks to Ildar Muslukhov.


## [v0.7.1] - 2009-04-05

### Added
- Added `crc-32mpeg`. Thanks to Thomas Edwards.


## [v0.7] - 2009-02-27

### Added
- Added the `--direct` option.
- Added `--check-hexstring` option. Closes issue 2545183.
  Thanks to Arnim Littek.
- Added a check for extra arguments on the command line.
  Closes issue 2545185. Thanks to Arnim Littek.

### Changed
- Added one more example in the documentation.


## [v0.6.7] - 2008-12-11

### Changed
- Run Python's 2to3 script on all files.
  Check the code on a x64 platform.
- Fixed a bug that raised an exception when an unknown model was selected.


## [v0.6.6] - 2008-06-05

### Changed
- New license for the documentation:
  [Creative Commons Attribution-Share Alike 3.0 Unported License][CC-BY-SA-3.0].

### Fixed
- Fixed a bug in the `print_params()` function. Closes issue 1985197.
  Thanks to Artur Lipowski.


## [v0.6.5] - 2008-03-03

### Added
- Added dallas-1-wire 8 bit CRC.
- Added `r-crc-16 model` (DECT (cordless digital standard) packets A-field
  according to ETSI EN 300 175-3 v2.1.1).
  Thanks to "raimondo".
- Added `--crc-type` and `--include-file` options.
- Added new file to handle CRC models.

### Changed
- Added extern "C" declaration to the generated C header file.
  Thanks to Nathan Royer.
- Changed the API to take the CRC model direct as parameter. Deleted the need
  for an obscure `opt` object.

### Fixed
- Fixed a problem with the generated code for bit-by-bit-fast algorithms.
  Thanks to Hans Bacher.


## [v0.6.4] - 2007-12-05

### Fixed
- Fixed a bug in the code generator for the `table-driven`
  algorithm. Thanks to Tom McDermott. Closes issue 1843774


## [v0.6.3] - 2007-10-13

### Added
- Added new models: `crc-5`, `crc-15`, `crc-16-usb`, `crc-24`, `crc-64`.
  The new models are taken from Ray Burr's CrcMoose.

### Fixed
- Fixed some portability problems in the generated code.
  Thanks to Helmut Bauer. Closes issue 1812894.
- The option `--check-file` works now with `--width` < 8. Closes issue 1794343.
- Removed unnecessary restriction on the width when using the `bit-by-bit-fast`
  algorithm. Closes issue 1794344.


## [v0.6.2] - 2007-08-25

### Changed
- Simplified the table-driven code. Closes issue 1727128.
- Changed the macro language syntax to a better format.
- Renamed `crc_code_gen.py` to `crc_parser.py`.
- Documented the usage of the `crc_*` modules.

### Fixed
- The parameter to `--check-string` was ignored. Closes issue 1781637.


## [v0.6.1] - 2007-08-12

### Added
- Added test for C89 compilation.
- Added a test case to loop over the input bytes one by one.

### Removed
- Deleted obsolete options.

### Changed
- Tidied up the documentation.
  Code cleanup.

### Fixed
- Bugfix in the source code generator for C89:
  Compilation error due to mismatch of parameters in the `crc_finalize`
  funtion.
- Changes related to 919107: Code generator includes `reflect()` function even
  if not needed.
- Fixed a typo in the C89 source code generator.
  Thanks to Helmut Bauer.


## [v0.6] - 2007-05-21

### Added
- Added the `--std` option to generate C89 (ANSI) compliant code.
- Added a new check to the test script which validate all possible
  combination of undefined parameters.
- Made the generated main function cope with command line arguments.
- Added the `--generate` table option.
- Added a template engine for the code generation. Split up `pycrc.py` into
  smaller modules.
- Added obsolete options again tor legacy reasons.
- Added a better handling of the `--model` parameter.

### Changed
- Reduced the size of the symbol table by re-arranging items.
- Changed licence to the MIT licence. This makes the additional clause for
  generated source code obsolete.
  Changed all command line options with underscores to hyphen (e.g.
  `table_driven` becomes `table-driven`).
  Added the option `--generate` which obsoletes the old options `--generate_c`
  `--generate_h` etc.


## [v0.5] - 2007-03-25

### Fixed
- Fixed bug 1686404: unhandled exception when called with both options
  `--table_idx_width` and `--check_file`.
- Eliminated useless declaration of `crc_reflect`, when not used.
- Corrected typos in the documentation.


## [v0.4] - 2007-01-26

### Added
- Added more parameter sets (now supported: `crc-8`, `crc-16`, `citt`, `kermit`,
  `x-25`, `xmodem`, `zmodem`, `crc-32`, `crc-32c`, `posix`, `jam`, `xfer`) from
  [Greg Cook's Catalogue of parametrised CRC algorithms][crc catalogue].
- Added Doxygen documentation strings to the functions.
- Added the `--symbol_prefix` option.
- Added the `--check_file` option.
- Added a non-regression test on the generated C source.

### Changed
- Eliminated needless documentation of not generated functions.
- Many corrections to the manual (thanks Francesca) Documented the new
  parameter sets.
- Added some new tests, disabled the random loop.

### Fixed
- Corrected many typos and bad phrasing (still a lot to do) Documented the
  `--symbol_prefix` option.


## [v0.3] - 2007-01-14

### Added
- First public release pycrc v0.3



[Unreleased]: https://github.com/tpircher/pycrc
[v0.9.1]: https://github.com/tpircher/pycrc/releases/tag/v0.9.1
[v0.9]: https://github.com/tpircher/pycrc/releases/tag/v0.9
[v0.8.3]: https://github.com/tpircher/pycrc/releases/tag/v0.8.3
[v0.8.2]: https://github.com/tpircher/pycrc/releases/tag/v0.8.2
[v0.8.1]: https://github.com/tpircher/pycrc/releases/tag/v0.8.1
[v0.8]: https://github.com/tpircher/pycrc/releases/tag/v0.8
[v0.7.11]: https://github.com/tpircher/pycrc/releases/tag/v0.7.11
[v0.7.10]: https://github.com/tpircher/pycrc/releases/tag/v0.7.10
[v0.7.9]: https://github.com/tpircher/pycrc/releases/tag/v0.7.9
[v0.7.8]: https://github.com/tpircher/pycrc/releases/tag/v0.7.8
[v0.7.7]: https://github.com/tpircher/pycrc/releases/tag/v0.7.7
[v0.7.6]: https://github.com/tpircher/pycrc/releases/tag/v0.7.6
[v0.7.5]: https://github.com/tpircher/pycrc/releases/tag/v0.7.5
[v0.7.4]: https://github.com/tpircher/pycrc/releases/tag/v0.7.4
[v0.7.3]: https://github.com/tpircher/pycrc/releases/tag/v0.7.3
[v0.7.2]: https://github.com/tpircher/pycrc/releases/tag/v0.7.2
[v0.7.1]: https://github.com/tpircher/pycrc/releases/tag/v0.7.1
[v0.7]: https://github.com/tpircher/pycrc/releases/tag/v0.7
[v0.6.7]: https://github.com/tpircher/pycrc/releases/tag/v0.6.7
[v0.6.6]: https://github.com/tpircher/pycrc/releases/tag/v0.6.6
[v0.6.5]: https://github.com/tpircher/pycrc/releases/tag/v0.6.5
[v0.6.4]: https://github.com/tpircher/pycrc/releases/tag/v0.6.4
[v0.6.3]: https://github.com/tpircher/pycrc/releases/tag/v0.6.3
[v0.6.2]: https://github.com/tpircher/pycrc/releases/tag/v0.6.2
[v0.6.1]: https://github.com/tpircher/pycrc/releases/tag/v0.6.1
[v0.6]: https://github.com/tpircher/pycrc/releases/tag/v0.6
[v0.5]: https://github.com/tpircher/pycrc/releases/tag/v0.5
[v0.4]: https://github.com/tpircher/pycrc/releases/tag/v0.4
[v0.3]: https://github.com/tpircher/pycrc/releases/tag/v0.3

[pycrc home]: https://pycrc.org
[pycrc github]: https://github.com/tpircher/pycrc
[pycrc issues]: https://github.com/tpircher/pycrc/issues
[crc catalogue]: http://regregex.bbcmicro.net/crc-catalogue.htm
[universal crc]: http://mcgougan.se/universal_crc/
[qm github]: https://github.com/tpircher/quine-mccluskey
[CC-BY-SA-3.0]: https://creativecommons.org/licenses/by-sa/3.0/
[CC-BY-SA-4.0]: https://creativecommons.org/licenses/by-sa/4.0/
