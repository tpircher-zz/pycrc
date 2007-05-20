#!/bin/sh
set -e

PYCRC=`dirname $0`/../pycrc.py

STD_TEST=1
CHECK_COMPILED=1
COMPILE_FIXED=0
CHECK_FILE=0
DO_RANDOM_LOOP=0
TEST_ARGS_COMPILATION=0


function testres {
    lcmd="$1"
    lres="$2"
    lres=`echo $lres | sed -e      's/.*0x0*\([0-9a-fA-F][0-9a-fA-F]*\).*/\1/'`
    lclc=`$lcmd      | sed -e '$!d; s/.*0x0*\([0-9a-fA-F][0-9a-fA-F]*\).*/\1/'`
    if [ "$lclc" != "$lres" ]; then
        echo >&2 test failed: $lcmd 
        echo >&2 got $lclc instead of expected $lres
        return 1
    fi
}


function teststr {
    lopt="$1 --check-string 123456789"
    lres="$2"
    testres "$lopt" "$lres"
}


function compile {
    lalg="$1"
    lopt="$2"
    lout="$3"

    $PYCRC --algorithm "$lalg" $lopt --generate h -o crc.h
    ldef=`echo "$lopt" | egrep -c 'width|poly|reflect|xor'` || true
    if [ "$ldef" -eq 0 ]; then
        $PYCRC --algorithm "$lalg" $lopt --generate c -o crc.c
        gcc -W -Wall -pedantic -std=c99 main.c crc.c -o "$lout"
    else
        $PYCRC --algorithm "$lalg" $lopt --generate c-main -o crc.c
        gcc -W -Wall -pedantic -std=c99 crc.c -o "$lout"
    fi
}


function testcmp {
    lalg="$1"
    lopt="$2"
    larg="$3"
    lres="$4"

    compile "$lalg" "$lopt" "a.out"
    testres "./a.out $larg" "$lres"
}


function testbin {
    lopt="$1"
    lres="$2"

    if [ "$CHECK_COMPILED" -ne 0 ]; then
        testres "./crc-bb  $lopt" "$lres"
        testres "./crc-bf  $lopt" "$lres"
        testres "./crc-td2 $lopt" "$lres"
        testres "./crc-td4 $lopt" "$lres"
        testres "./crc-td8 $lopt" "$lres"

        if [ "$COMPILE_FIXED" -ne 0 ]; then
            testcmp bit-by-bit "$lopt" "" "$lres"
            testcmp bit-by-bit-fast "$lopt" "" "$lres"
            testcmp table-driven "$lopt --table-idx-width 2" "" "$lres"
            testcmp table-driven "$lopt --table-idx-width 4" "" "$lres"
            testcmp table-driven "$lopt --table-idx-width 8" "" "$lres"
        fi
    fi
}


function testfil {
    lopt="$1 --check-file file.txt"
    lres="$2"

    if [ "$CHECK_FILE" -ne 0 ]; then
        testres "$lopt" "$lres"
    fi
}


if [ "$CHECK_COMPILED" -ne 0 ]; then
    compile "bit-by-bit" "" "crc-bb"
    compile "bit-by-bit-fast" "" "crc-bf"
    compile "table-driven" "--table-idx-width 2" "crc-td2"
    compile "table-driven" "--table-idx-width 4" "crc-td4"
    compile "table-driven" "--table-idx-width 8" "crc-td8"
fi
if [ ! -f file.txt ]; then
    echo -n "123456789" > file.txt
fi


if [ "$STD_TEST" -ne 0 ]; then
#CRC-8
res="0xf4"
cmd="$PYCRC --model crc-8"
opt="--width 8 --poly 0x07 --reflect-in 0 --xor-in 0x0 --reflect-out 0 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16/ARC
res="0xbb3d"
cmd="$PYCRC --model crc-16"
opt="--width 16 --poly 0x8005 --reflect-in 1 --xor-in 0x0 --reflect-out 1 --xor-out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16/CITT
res="0x29b1"
cmd="$PYCRC --model citt"
opt="--width 16 --poly 0x1021 --reflect-in 0 --xor-in 0xffff --reflect-out 0 --xor-out 0x0"
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
res="0x0c73"
cmd="$PYCRC --model xmodem"
opt="--width 16 --poly 0x8408 --reflect-in 1 --xor-in 0x0 --reflect-out 1 --xor-out 0x0"
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
opt="--width 32 --poly 0x04c11db7 --reflect-in 1 --xor-in 0xffffffff --reflect-out 1 --xor-out 0x0"
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
fi


if [ "$DO_RANDOM_LOOP" -ne 0 ]; then
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


if [ "$TEST_ARGS_COMPILATION" -ne 0 ]; then
    #zmodem
    res="0x31c3"
    opt_width="--width 16"
    opt_poly="--poly 0x1021"
    opt_refin="--reflect-in 0"
    opt_xorin="--xor-in 0x0"
    opt_refout="--reflect-out 0"
    opt_xorout="--xor-out 0x0"
    for width in 0 1; do
        if [ "$width" -eq 1 ]; then cmp_width="$opt_width"; arg_width=""; else cmp_width=""; arg_width="$opt_width"; fi
        for poly in 0 1; do
            if [ "$poly" -eq 1 ]; then cmp_poly="$opt_poly"; arg_poly=""; else cmp_poly=""; arg_poly="$opt_poly"; fi
            for ref_in in 0 1; do
                if [ "$ref_in" -eq 1 ]; then cmp_refin="$opt_refin"; arg_refin=""; else cmp_refin=""; arg_refin="$opt_refin"; fi
                for ref_out in 0 1; do
                    if [ "$ref_out" -eq 1 ]; then cmp_refout="$opt_refout"; arg_refout=""; else cmp_refout=""; arg_refout="$opt_refout"; fi
                    for xor_in in 0 1; do
                        if [ "$xor_in" -eq 1 ]; then cmp_xorin="$opt_xorin"; arg_xorin=""; else cmp_xorin=""; arg_xorin="$opt_xorin"; fi
                        for xor_out in 0 1; do
                            if [ "$xor_out" -eq 1 ]; then cmp_xorout="$opt_xorout"; arg_xorout=""; else cmp_xorout=""; arg_xorout="$opt_xorout"; fi
                            cmp_opt="$cmp_width $cmp_poly $cmp_refin $cmp_refout $cmp_xorin $cmp_xorout"
                            arg_opt="$arg_width $arg_poly $arg_refin $arg_refout $arg_xorin $arg_xorout"
                            echo $cmp_opt
                            echo $arg_opt
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

rm -f crc.c crc.h a.out crc-bb crc-bf crc-td2 crc-td4 crc-td8 file.txt
echo Test OK
