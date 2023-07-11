#!/bin/bash

set -e

test_disassembling_a_file() {
    local verbose
    if [ "$1" == verbose ]; then
        verbose=-v
        echo -e "Testing disassembling a file in VERBOSE mode"
    else
        echo -e "Testing disassembling a file in NORMAL mode"
    fi

    testname=all_opcodes
    fixture=fixtures/${testname}.S
    echo -e "\tBuilding $fixture using micropython-esp32-ulp"

    log_file="${testname}.log"
    ulp_file="fixtures/${testname}.ulp"
    micropython -m esp32_ulp $fixture 1>$log_file   # generates $ulp_file

    lst_file="${testname}.lst"
    lst_file_fixture=fixtures/${testname}${verbose}.lst
    echo -e "\tDisassembling $ulp_file using micropython-esp32-ulp disassembler"
    micropython -m tools.disassemble $verbose $ulp_file > $lst_file

    if ! diff $lst_file_fixture $lst_file 1>/dev/null; then
        echo -e "\tDisassembled output differs from expected output!"
        echo ""
        echo "Disassembly test failed for $fixture"
        echo "micropython-esp32-ulp log:"
        cat $log_file
        echo "Diff of disassembly: expected vs actual"
        diff -u $lst_file_fixture $lst_file
    fi
}

test_disassembling_a_manual_sequence() {
    local verbose
    if [ "$1" == verbose ]; then
        verbose=-v
        echo -e "Testing disassembling a manual byte sequence in VERBOSE mode"
    else
        echo -e "Testing disassembling a manual byte sequence in NORMAL mode"
    fi

    sequence="e1af 8c72 0100 0068 2705 cc19 0005 681d 0000 00a0 0000 0074"

    lst_file="manual_bytes.lst"
    lst_file_fixture=fixtures/manual_bytes${verbose}.lst
    echo -e "\tDisassembling manual byte sequence using micropython-esp32-ulp disassembler"
    micropython -m tools.disassemble $verbose -m $sequence > $lst_file

    if ! diff $lst_file_fixture $lst_file 1>/dev/null; then
        echo -e "\tDisassembled output differs from expected output!"
        echo ""
        echo "Disassembly test failed for manual byte sequence"
        echo "Diff of disassembly: expected vs actual"
        diff -u $lst_file_fixture $lst_file
    fi
}

test_disassembling_a_file
test_disassembling_a_file verbose

test_disassembling_a_manual_sequence
test_disassembling_a_manual_sequence verbose
