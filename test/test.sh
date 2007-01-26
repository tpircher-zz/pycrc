#!/bin/sh
set -e

PYCRC=`dirname $0`/../pycrc.py

CHECK_COMPILED=1
COMPILE_FIXED=1
CHECK_FILE=1
DO_RANDOM_LOOP=0


function testres {
    lcmd="$1"
    lres="$2"
    lres=`echo $lres | sed -e      's/.*0x0*\([0-9a-fA-F]*\).*/\1/'`
    lclc=`$lcmd      | sed -e '$!d; s/.*0x0*\([0-9a-fA-F]*\).*/\1/'`
    if [ "$lclc" != "$lres" ]; then
        echo >&2 test failed: $lcmd 
        echo >&2 got $lclc instead of expected $lres
        return 1
    fi
}


function teststr {
    lopt="$1 --check_string 123456789"
    lres="$2"
    testres "$lopt" "$lres"
}


function compile {
    lalg="$1"
    lopt="$2"
    lout="$3"

    $PYCRC --algorithm "$lalg" $lopt --generate_h -o crc.h
    ldef=`echo "$lopt" | grep -c poly` && true
    if [ "$ldef" -eq 0 ]; then
        $PYCRC --algorithm "$lalg" --generate_c -o crc.c
        gcc -W -Wall -pedantic -std=c99 main.c crc.c -o "$lout"
    else
        $PYCRC --algorithm "$lalg" $lopt --generate_c_main -o crc.c
        gcc -W -Wall -pedantic -std=c99 crc.c -o "$lout"
    fi
}


function testcmp {
    lalg="$1"
    lopt="$2"
    lres="$3"

    compile "$lalg" "$lopt" "a.out"
    testres "./a.out $lopt" "$lres"
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
            testcmp bit_by_bit "$lopt" "$lres"
            testcmp bit_by_bit_fast "$lopt" "$lres"
            testcmp table_driven "$lopt --table_idx_with 2" "$lres"
            testcmp table_driven "$lopt --table_idx_with 4" "$lres"
            testcmp table_driven "$lopt --table_idx_with 8" "$lres"
        fi
    fi
}


function testfil {
    lopt="$1 --check_file file.txt"
    lres="$2"

    if [ "$CHECK_FILE" -ne 0 ]; then
        testres "$lopt" "$lres"
    fi
}


if [ "$CHECK_COMPILED" -ne 0 ]; then
    compile "bit_by_bit" "" "crc-bb"
    compile "bit_by_bit_fast" "" "crc-bf"
    compile "table_driven" "--table_idx_with 2" "crc-td2"
    compile "table_driven" "--table_idx_with 4" "crc-td4"
    compile "table_driven" "--table_idx_with 8" "crc-td8"
fi
if [ ! -f file.txt ]; then
    echo -n "123456789" > file.txt
fi


#CRC-8
res="0xf4"
cmd="$PYCRC --model crc-8"
opt="--width 8 --poly 0x07 --reflect_in 0 --xor_in 0x0 --reflect_out 0 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16/ARC
res="0xbb3d"
cmd="$PYCRC --model crc-16"
opt="--width 16 --poly 0x8005 --reflect_in 1 --xor_in 0x0 --reflect_out 1 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-16/CITT
res="0x29b1"
cmd="$PYCRC --model citt"
opt="--width 16 --poly 0x1021 --reflect_in 0 --xor_in 0xffff --reflect_out 0 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#kermit
res="0x2189"
cmd="$PYCRC --model kermit"
opt="--width 16 --poly 0x1021 --reflect_in 1 --xor_in 0x0 --reflect_out 1 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#X-25
res="0x906e"
cmd="$PYCRC --model x-25"
opt="--width 16 --poly 0x1021 --reflect_in 1 --xor_in 0xffff --reflect_out 1 --xor_out 0xffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#xmodem
res="0x0c73"
cmd="$PYCRC --model xmodem"
opt="--width 16 --poly 0x8408 --reflect_in 1 --xor_in 0x0 --reflect_out 1 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#zmodem
res="0x31c3"
cmd="$PYCRC --model zmodem"
opt="--width 16 --poly 0x1021 --reflect_in 0 --xor_in 0x0 --reflect_out 0 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32
res="0xcbf43926"
cmd="$PYCRC --model crc-32"
opt="--width 32 --poly 0x4c11db7 --reflect_in 1 --xor_in 0xffffffff --reflect_out 1 --xor_out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32C
res="0xe3069283"
cmd="$PYCRC --model crc-32c"
opt="--width 32 --poly 0x1edc6f41 --reflect_in 1 --xor_in 0xffffffff --reflect_out 1 --xor_out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#CRC-32/POSIX
res="0x765e7680"
cmd="$PYCRC --model posix"
opt="--width 32 --poly 0x4c11db7 --reflect_in 0 --xor_in 0x0 --reflect_out 0 --xor_out 0xffffffff"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#JAMCRC
res="0x340bc6d9"
cmd="$PYCRC --model jam"
opt="--width 32 --poly 0x04c11db7 --reflect_in 1 --xor_in 0xffffffff --reflect_out 1 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"

#XFER
res="0xbd0be338"
cmd="$PYCRC --model xfer"
opt="--width 32 --poly 0x000000af --reflect_in 0 --xor_in 0x0 --reflect_out 0 --xor_out 0x0"
teststr "$cmd" "$res"
teststr "$PYCRC $opt" "$res"
testfil "$cmd" "$res"
testbin "$opt" "$res"


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


rm -f crc.c crc.h a.out crc-bb crc-bf crc-td2 crc-td4 crc-td8 file.txt
echo Test OK
