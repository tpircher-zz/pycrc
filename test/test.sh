#!/bin/sh
set -e

PYCRC=`dirname $0`/../pycrc.py

CHECK_COMPILED=1
COMPILE_FIXED=1
DO_RANDOM_LOOP=1

function testcrc {
    command="$1 --check_string 123456789"
    result="$2"
    calc=`$command     | sed -e '$!d; s/.*0x0*\([0-9a-fA-F]*\).*/\1/'`
    resu=`echo $result | sed -e      's/.*0x0*\([0-9a-fA-F]*\).*/\1/'`
    if [ "$calc" != "$resu" ]; then
        echo >&2 test failed: $command 
        echo >&2 got $calc instead of expected $result
        return 1
    fi
}


function compile {
    alg="$1"
    opt="$2"
    out="$3"

    $PYCRC --algorithm "$alg" $opt --generate_h -o crc.h
    def=`echo "$opt" | grep -c poly` && true
    if [ "$def" -eq 0 ]; then
        $PYCRC --algorithm "$alg" --generate_c -o crc.c
        gcc -W -Wall -pedantic -std=c99 main.c crc.c -o "$out"
    else
        $PYCRC --algorithm "$alg" $opt --generate_c_main -o crc.c
        gcc -W -Wall -pedantic -std=c99 crc.c -o "$out"
    fi
}


function testcmp {
    alg="$1"
    opt="$2"
    res="$3"

    compile "$alg" "$opt" "a.out"
    testcrc "./a.out $opt" "$res"
}


function testbin {
    opt="$1"
    res="$2"

    if [ "$CHECK_COMPILED" -ne 0 ]; then
        testcrc "./crc-bb  $opt" "$res"
        testcrc "./crc-bf  $opt" "$res"
        testcrc "./crc-td2 $opt" "$res"
        testcrc "./crc-td4 $opt" "$res"
        testcrc "./crc-td8 $opt" "$res"

        if [ "$COMPILE_FIXED" -ne 0 ]; then
            testcmp bit_by_bit "$opt" "$res"
            testcmp bit_by_bit_fast "$opt" "$res"
            testcmp table_driven "$opt --table_idx_with 2" "$res"
            testcmp table_driven "$opt --table_idx_with 4" "$res"
            testcmp table_driven "$opt --table_idx_with 8" "$res"
        fi
    fi
}


if [ "$CHECK_COMPILED" -ne 0 ]; then
    compile "bit_by_bit" "" "crc-bb"
    compile "bit_by_bit_fast" "" "crc-bf"
    compile "table_driven" "--table_idx_with 2" "crc-td2"
    compile "table_driven" "--table_idx_with 4" "crc-td4"
    compile "table_driven" "--table_idx_with 8" "crc-td8"
fi

if [ "$DO_RANDOM_LOOP" -ne 0 ]; then
    for width in 8 16 32; do
        for poly in 0x8005 0x4c11db7 0xa5a5a5a5; do
            for refxx in "--reflect_in 0 --reflect_out 0" "--reflect_in 0 --reflect_out 1" "--reflect_in 1 --reflect_out 0" "--reflect_in 1 --reflect_out 1"; do
                for init in 0x0 0x1 0xa5a5a5a5; do
                    opt="--width $width --poly $poly $refxx --xor_in $init --xor_out 0x0"
                    cmd="$PYCRC $opt"
                    res=`$cmd` || $cmd
                    testbin "$opt" "$res"
                done
            done
        done
    done
fi


#CRC-8
res="0xf4"
cmd="$PYCRC --model crc-8 --check_string 123456789"
opt="--width 8 --poly 0x07 --reflect_in 0 --xor_in 0x0 --reflect_out 0 --xor_out 0x0"
testcrc "$cmd" "$res"
testcrc "$PYCRC $opt" "$res"
testbin "$opt" "$res"

#CRC-16/CITT
res="0xbb3d"
cmd="$PYCRC --model crc-16 --check_string 123456789"
opt="--width 16 --poly 0x8005 --reflect_in 1 --xor_in 0x0 --reflect_out 1 --xor_out 0x0"
testcrc "$cmd" "$res"
testcrc "$PYCRC $opt" "$res"
testbin "$opt" "$res"

#xmodem
res="0x0c73"
cmd="$PYCRC --model xmodem --check_string 123456789"
opt="--width 16 --poly 0x8408 --reflect_in 1 --xor_in 0x0 --reflect_out 1 --xor_out 0x0"
testcrc "$cmd" "$res"
testcrc "$PYCRC $opt" "$res"
testbin "$opt" "$res"

#CRC-32
res="0xcbf43926"
cmd="$PYCRC --model crc-32 --check_string 123456789"
opt="--width 32 --poly 0x4c11db7 --reflect_in 1 --xor_in 0xffffffff --reflect_out 1 --xor_out 0xffffffff"
testcrc "$cmd" "$res"
testcrc "$PYCRC $opt" "$res"
testbin "$opt" "$res"

rm -f crc.c crc.h a.out crc-bb crc-bf crc-td2 crc-td4 crc-td8
echo Test OK
