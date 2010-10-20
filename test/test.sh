#!/bin/bash
set -e

PYCRC=`dirname $0`/../pycrc.py

usage() {
        echo >&2 "usage: $0 [OPTIONS]"
        echo >&2 ""
        echo >&2 "with OPTIONS in"
        echo >&2 "        -c    test compiled version"
        echo >&2 "        -n    test compiled version with fixed parameters"
        echo >&2 "        -f    test file"
        echo >&2 "        -r    test random parameters"
        echo >&2 "        -p    test compiled C program with random arguments"
        echo >&2 "        -w    test variable width from 1 to 64"
        echo >&2 "        -a    do all tests"
}


crc_std_test=on
crc_compiled_test=off
crc_compile_noparam_test=off
crc_file_test=off
crc_random_loop_test=off
crc_args_compile_test=off
crc_variable_width_test=off
crc_all_tests=off

while getopts cnfrpwah opt; do
    case "$opt" in
        c)  crc_compiled_test=on;;
        n)  crc_compile_noparam_test=on;;
        f)  crc_file_test=on;;
        r)  crc_random_loop_test=on;;
        p)  crc_args_compile_test=on;;
        w)  crc_variable_width_test=on;;
        a)  crc_all_tests=on;;
        h)  usage
            exit 0
            ;;
        \?) usage       # unknown flag
            exit 1
            ;;
    esac
done
shift `expr $OPTIND - 1`


cleanup() {
    rm -f crc.c crc.h a.out crc-bb crc-bf crc-td2 crc-td4 crc-td8 file.txt
}

trap cleanup 0 1 2 3 15


testres() {
    testres_lcmd="$1"
    testres_lres="$2"
    testres_lres=`echo $testres_lres | sed -e      's/.*0x0*\([0-9a-fA-F][0-9a-fA-F]*\).*/\1/'`
    testres_lclc=`$testres_lcmd      | sed -e '$!d; s/.*0x0*\([0-9a-fA-F][0-9a-fA-F]*\).*/\1/'`
    if [ "$testres_lclc" != "$testres_lres" ]; then
        echo >&2 test failed: $testres_lcmd 
        echo >&2 got $testres_lclc instead of expected $testres_lres
        return 1
    fi
}


teststr() {
    teststr_lopt="$1 --check-string 123456789"
    teststr_lres="$2"
    testres "$teststr_lopt" "$teststr_lres"
}


compile() {
    compile_lalg="$1"
    compile_lopt="$2"
    compile_lout="$3"

    $PYCRC --algorithm "$compile_lalg" $compile_lopt --generate h -o crc.h
    ldef=`echo "$compile_lopt" | egrep -c 'width|poly|reflect|xor'` || true
    if [ "$ldef" -eq 0 ]; then
        $PYCRC --algorithm "$compile_lalg" $compile_lopt --generate c -o crc.c
        gcc -W -Wall -pedantic -std=c99 main.c crc.c -o "$compile_lout"
    else
        $PYCRC --algorithm "$compile_lalg" $compile_lopt --generate c-main -o crc.c
        gcc -W -Wall -pedantic -std=c99 crc.c -o "$compile_lout"
    fi
}


testcmp() {
    testcmp_lalg="$1"
    testcmp_lopt="$2"
    testcmp_larg="$3"
    testcmp_lres="$4"

    compile "$testcmp_lalg" "$testcmp_lopt --std C89" "a.out"
    testres "./a.out $testcmp_larg" "$testcmp_lres"

    compile "$testcmp_lalg" "$testcmp_lopt --std C99" "a.out"
    testres "./a.out $testcmp_larg" "$testcmp_lres"
}


testbin() {
    testbin_lopt="$1"
    testbin_lres="$2"

    if [ "$crc_compiled_test" == on -o "$crc_all_tests" == on ]; then
        testres "./crc-bb  $testbin_lopt" "$testbin_lres"
        testres "./crc-bf  $testbin_lopt" "$testbin_lres"
        testres "./crc-td2 $testbin_lopt" "$testbin_lres"
        testres "./crc-td4 $testbin_lopt" "$testbin_lres"
        testres "./crc-td8 $testbin_lopt" "$testbin_lres"

        if [ "$crc_compile_noparam_test" == on -o "$crc_all_tests" == on ]; then
            testcmp bit-by-bit "$testbin_lopt" "" "$testbin_lres"
            testcmp bit-by-bit-fast "$testbin_lopt" "" "$testbin_lres"
            testcmp table-driven "$testbin_lopt --table-idx-width 2" "" "$testbin_lres"
            testcmp table-driven "$testbin_lopt --table-idx-width 4" "" "$testbin_lres"
            testcmp table-driven "$testbin_lopt --table-idx-width 8" "" "$testbin_lres"
        fi
    fi
}


testfil() {
    testfil_lopt="$1 --check-file file.txt"
    testfil_lres="$2"

    if [ "$crc_file_test" == on -o "$crc_all_tests" == on ]; then
        testres "$testfil_lopt" "$testfil_lres"
    fi
}


if [ "$crc_compiled_test" == on -o "$crc_all_tests" == on ]; then
    compile "bit-by-bit" "" "crc-bb"
    compile "bit-by-bit-fast" "" "crc-bf"
    compile "table-driven" "--table-idx-width 2" "crc-td2"
    compile "table-driven" "--table-idx-width 4" "crc-td4"
    compile "table-driven" "--table-idx-width 8" "crc-td8"
fi
if [ ! -f file.txt ]; then
    echo -n "123456789" > file.txt
fi


if [ "$crc_std_test" == on -o "$crc_all_tests" == on ]; then
#CRC-5
res="0x19"
cmd="$PYCRC --model crc-5"
opt="--width 5 --poly 0x05 --reflect-in 1 --xor-in 0x1f --reflect-out 1 --xor-out 0x1f"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
#testbin "$opt" "$res"      # don't test binaries with Width < 8 (table driven algorithm does not work)

#CRC-8
res="0xf4"
cmd="$PYCRC --model crc-8"
opt="--width 8 --poly 0x07 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#DALLAS-1-WIRE
res="0xa1"
cmd="$PYCRC --model dallas-1-wire"
opt="--width 8 --poly 0x31 --reflect-in 1 --xor-in 0 --reflect-out 1 --xor-out 0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-15
res="0x59e"
cmd="$PYCRC --model crc-15"
opt="--width 15 --poly 0x4599 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
#testbin "$opt" "$res"      # don't test binaries with width not a multiple of 8 (table driven algorithm does not work)

#CRC-16/ARC
res="0xbb3d"
cmd="$PYCRC --model crc-16"
opt="--width 16 --poly 0x8005 --reflect-in 1 --xor-in 0x0 --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16-USB
res="0xb4c8"
cmd="$PYCRC --model crc-16-usb"
opt="--width 16 --poly 0x8005 --reflect-in 1 --xor-in 0xffff --reflect-out 1 --xor-out 0xffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16-MODBUS
res="0x4b37"
cmd="$PYCRC --model crc-16-modbus"
opt="--width 16 --poly 0x8005 --reflect-in 1 --xor-in 0xffff --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16/CITT
res="0x29b1"
cmd="$PYCRC --model ccitt"
opt="--width 16 --poly 0x1021 --reflect-in 0 --xor-in 0xffff --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#R-CRC-16/DECT packets A-field according to ETSI EN 300 175-3 v2.1.1
res="0x007e"
cmd="$PYCRC --model r-crc-16"
opt="--width 16 --poly 0x0589 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0001"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#kermit
res="0x2189"
cmd="$PYCRC --model kermit"
opt="--width 16 --poly 0x1021 --reflect-in 1 --xor-in 0x0 --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#X-25
res="0x906e"
cmd="$PYCRC --model x-25"
opt="--width 16 --poly 0x1021 --reflect-in 1 --xor-in 0xffff --reflect-out 1 --xor-out 0xffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#xmodem
res="0x31c3"
cmd="$PYCRC --model xmodem"
opt="--width 16 --poly 0x1021 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#zmodem
res="0x31c3"
cmd="$PYCRC --model zmodem"
opt="--width 16 --poly 0x1021 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#crc-24
res="0x21cf02"
cmd="$PYCRC --model crc-24"
opt="--width 24 --poly 0x1864cfb --reflect-in 0 --xor-in 0xb704ce --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
#testbin "$opt" "$res"      # don't test binaries with width not a multiple of 8 (table driven algorithm does not work)

#CRC-32
res="0xcbf43926"
cmd="$PYCRC --model crc-32"
opt="--width 32 --poly 0x4c11db7 --reflect-in 1 --xor-in 0xffffffff --reflect-out 1 --xor-out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32C
res="0xe3069283"
cmd="$PYCRC --model crc-32c"
opt="--width 32 --poly 0x1edc6f41 --reflect-in 1 --xor-in 0xffffffff --reflect-out 1 --xor-out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32/POSIX
res="0x765e7680"
cmd="$PYCRC --model posix"
opt="--width 32 --poly 0x4c11db7 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#JAMCRC
res="0x340bc6d9"
cmd="$PYCRC --model jam"
opt="--width 32 --poly 0x4c11db7 --reflect-in 1 --xor-in 0xffffffff --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32MPEG
res="0x376e6e7"
cmd="$PYCRC --model crc-32-mpeg"
opt="--width 32 --poly 0x4c11db7 --reflect-in 0 --xor-in 0xffffffff --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#XFER
res="0xbd0be338"
cmd="$PYCRC --model xfer"
opt="--width 32 --poly 0x000000af --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-64
res="0x46a5a9388a5beffe"
cmd="$PYCRC --model crc-64"
opt="--width 64 --poly 0x000000000000001b --reflect-in 1 --xor-in 0x0 --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
#testbin "$opt" "$res"      # don't test binaries with width 64 bits (variables not wide enough...)

#CRC-64-jones
res="0xcaa717168609f281"
cmd="$PYCRC --model crc-64-jones"
opt="--width 64 --poly 0xad93d23594c935a9 --reflect-in 1 --xor-in 0xffffffffffffffff --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
#testbin "$opt" "$res"      # don't test binaries with width 64 bits (variables not wide enough...)
fi


if [ "$crc_random_loop_test" == on -o "$crc_all_tests" == on ]; then
    for width in 8 16 32; do
        for poly in 0x8005 0x4c11db7 0xa5a5a5a5; do
            for refxx in "--reflect-in 0 --reflect-out 0" "--reflect-in 0 --reflect-out 1" "--reflect-in 1 --reflect-out 0" "--reflect-in 1 --reflect-out 1"; do
                for init in 0x0 0x1 0xa5a5a5a5; do
                    opt="--width $width --poly $poly $refxx --xor-in $init --xor-out 0x0"
                    cmd="$PYCRC $opt"
                    res=`$cmd` || $cmd
                    testbin "$opt" "$res"
                done
            done
        done
    done
fi


if [ "$crc_args_compile_test" == on -o "$crc_all_tests" == on ]; then
    #zmodem
    res="0x31c3"
    opt_width="--width 16"
    opt_poly="--poly 0x1021"
    opt_refin="--reflect-in 0"
    opt_xorin="--xor-in 0x0"
    opt_refout="--reflect-out 0"
    opt_xorout="--xor-out 0x0"
    for b_width in 0 1; do
        if [ "$b_width" -eq 1 ]; then cmp_width="$opt_width"; arg_width=""; else cmp_width=""; arg_width="$opt_width"; fi
        for b_poly in 0 1; do
            if [ "$b_poly" -eq 1 ]; then cmp_poly="$opt_poly"; arg_poly=""; else cmp_poly=""; arg_poly="$opt_poly"; fi
            for b_ref_in in 0 1; do
                if [ "$b_ref_in" -eq 1 ]; then cmp_refin="$opt_refin"; arg_refin=""; else cmp_refin=""; arg_refin="$opt_refin"; fi
                for b_ref_out in 0 1; do
                    if [ "$b_ref_out" -eq 1 ]; then cmp_refout="$opt_refout"; arg_refout=""; else cmp_refout=""; arg_refout="$opt_refout"; fi
                    for b_xor_in in 0 1; do
                        if [ "$b_xor_in" -eq 1 ]; then cmp_xorin="$opt_xorin"; arg_xorin=""; else cmp_xorin=""; arg_xorin="$opt_xorin"; fi
                        for b_xor_out in 0 1; do
                            if [ "$b_xor_out" -eq 1 ]; then cmp_xorout="$opt_xorout"; arg_xorout=""; else cmp_xorout=""; arg_xorout="$opt_xorout"; fi

                            cmp_opt="$cmp_width $cmp_poly $cmp_refin $cmp_refout $cmp_xorin $cmp_xorout"
                            arg_opt="$arg_width $arg_poly $arg_refin $arg_refout $arg_xorin $arg_xorout"
                            testcmp bit-by-bit "$cmp_opt" "$arg_opt" "$res"
                            testcmp bit-by-bit-fast "$cmp_opt" "$arg_opt" "$res"
                            testcmp table-driven "$cmp_opt" "$arg_opt" "$res"
                        done
                    done
                done
            done
        done
    done
fi


if [ "$crc_variable_width_test" == on -o "$crc_all_tests" == on ]; then
    opt_poly="--poly 0xad93d23594c935a9"
    opt_refin="--reflect-in 1"
    opt_xorin="--xor-in 0xffffffffffffffff"
    opt_refout="--reflect-out 1"
    opt_xorout="--xor-out 0x0000000000000000"
    for width in 1 2 3 4 5 6 7 8 9 11 12 15 16 17 24 31 32 33 63 64; do
    for b_width in 0 1; do
        if [ "$b_width" -eq 1 ]; then cmp_width="--width $width"; arg_width=""; else cmp_width=""; arg_width="--width $width"; fi
        for b_poly in 0 1; do
            if [ "$b_poly" -eq 1 ]; then cmp_poly="$opt_poly"; arg_poly=""; else cmp_poly=""; arg_poly="$opt_poly"; fi
            for b_ref_in in 0 1; do
                if [ "$b_ref_in" -eq 1 ]; then cmp_refin="$opt_refin"; arg_refin=""; else cmp_refin=""; arg_refin="$opt_refin"; fi
                for b_ref_out in 0 1; do
                    if [ "$b_ref_out" -eq 1 ]; then cmp_refout="$opt_refout"; arg_refout=""; else cmp_refout=""; arg_refout="$opt_refout"; fi
                    for b_xor_in in 0 1; do
                        if [ "$b_xor_in" -eq 1 ]; then cmp_xorin="$opt_xorin"; arg_xorin=""; else cmp_xorin=""; arg_xorin="$opt_xorin"; fi
                        for b_xor_out in 0 1; do
                            if [ "$b_xor_out" -eq 1 ]; then cmp_xorout="$opt_xorout"; arg_xorout=""; else cmp_xorout=""; arg_xorout="$opt_xorout"; fi

                            cmp_opt="$cmp_width $cmp_poly $cmp_refin $cmp_refout $cmp_xorin $cmp_xorout"
                            arg_opt="$arg_width $arg_poly $arg_refin $arg_refout $arg_xorin $arg_xorout"
                            res=`$PYCRC --algorithm bit-by-bit $cmp_opt $arg_opt`
                            testcmp table-driven "$cmp_opt" "$arg_opt" "$res"
                        done
                    done
                done
            done
        done
    done
    done
fi

echo Test OK
