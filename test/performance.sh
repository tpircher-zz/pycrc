#!/bin/sh
set -e

PYCRC=`dirname $0`/../pycrc.py

cleanup() {
    rm -f a.out performance.c crc_bbb.[ch] crc_bbf.[ch] crc_tb[l4].[ch] crc_sb4.[ch]
}

trap cleanup 0 1 2 3 15

model=crc-32

prefix=bbb
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bit-by-bit
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bit-by-bit
prefix=bbf
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bit-by-bit-fast
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bit-by-bit-fast
prefix=tbl
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo table-driven
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo table-driven
prefix=tb4
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo table-driven --table-idx-width 4
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo table-driven --table-idx-width 4
prefix=sb4
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo table-driven --slice-by 4
$PYCRC --model $model --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo table-driven --slice-by 4


print_main() {
cat <<EOF
#include "crc_bbb.h"
#include "crc_bbf.h"
#include "crc_tbl.h"
#include "crc_tb4.h"
#include "crc_sb4.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/times.h>
#include <unistd.h>

#define NUM_RUNS    (128*256*256)

unsigned char buf[1024];

void test_bbb(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_bbf(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_tbl(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_tb4(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_sb4(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);

/**
 * Print results.
 *
 * \param   dsc Description of the test
 * \param   buflen Length of one buffer
 * \param   num_runs Number of runs over that buffer
 * \param   t_user user time
 * \param   t_sys system time
 * \return  void
 *****************************************************************************/
void show_times(const char *dsc, size_t buflen, size_t num_runs, double t_user)
{
    double mbps = (((double)buflen) * num_runs)/(1024*1024*t_user);
    printf("%s of %ld bytes (%ld * %ld)\n", dsc, (long)buflen*num_runs, (long)buflen, (long)num_runs);
    printf("%13s: %7.3f s %13s: %7.3f MiB/s\n", "user time", t_user, "throughput", mbps);
    printf("\n");
}


/**
 * C main function.
 *
 * \retval      0 on success
 * \retval      1 on failure
 *****************************************************************************/
int main(void)
{
    unsigned int i;
    long int clock_per_sec;

    for (i = 0; i < sizeof(buf); i++) {
        buf[i] = (unsigned char)rand();
    }
    clock_per_sec = sysconf(_SC_CLK_TCK);

    // bit-by-bit
    test_bbb(buf, sizeof(buf), NUM_RUNS / 8, clock_per_sec);

    // bit-by-bit-fast
    test_bbf(buf, sizeof(buf), NUM_RUNS / 8, clock_per_sec);

    // table-driven
    test_tbl(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // table-driven idx4
    test_tb4(buf, sizeof(buf), NUM_RUNS / 2, clock_per_sec);

    // table-driven slice-by 4
    test_sb4(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    return 0;
}
EOF
}

print_routine() {
    algo=$1
    prefix=$2
    cat <<EOF
/**
 * Test $algo Algorithm.
 *
 * \return      void
 *****************************************************************************/
void test_${prefix}(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec)
{
    crc_${prefix}_t crc;
    unsigned int i;
    struct tms tm1, tm2;

    times(&tm1);
    crc = crc_${prefix}_init();
    for (i = 0; i < num_runs; i++) {
        crc = crc_${prefix}_update(crc, buf, buf_len);
    }
    crc = crc_${prefix}_finalize(crc);
    times(&tm2);
    show_times("$model, $algo, block-wise", buf_len, num_runs,
            ((double)(tm2.tms_utime - tm1.tms_utime) / (double)clock_per_sec));
}

EOF
}

print_main > performance.c
print_routine "bit-by-bit" bbb >> performance.c
print_routine "bit-by-bit-fast" bbf >> performance.c
print_routine "table-driven" tbl >> performance.c
print_routine "table-driven idx4" tb4 >> performance.c
print_routine "table-driven sb4" sb4 >> performance.c

gcc -W -Wall -O3 crc_bbb.c crc_bbf.c crc_tbl.c crc_tb4.c crc_sb4.c performance.c
./a.out
