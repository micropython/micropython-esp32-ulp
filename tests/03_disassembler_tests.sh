#!/bin/bash

set -e

test_disassembling_a_file() {
    local cpu=$1
    local verbose
    if [ "$2" == verbose ]; then
        verbose=-v
        echo -e "Testing disassembling a file in VERBOSE mode"
    else
        echo -e "Testing disassembling a file in NORMAL mode"
    fi

    testname=all_opcodes
    fixture=fixtures/${testname}.S
    echo -e "\tBuilding $fixture using micropython-esp32-ulp ($cpu)"

    log_file="${testname}.log"
    ulp_file="fixtures/${testname}.ulp"
    micropython -m esp32_ulp -c $cpu $fixture 1>$log_file   # generates $ulp_file

    lst_file="${testname}.$cpu.lst"
    lst_file_fixture=fixtures/${testname}${verbose}.$cpu.lst
    echo -e "\tDisassembling $ulp_file using micropython-esp32-ulp disassembler ($cpu)"
    micropython -m tools.disassemble -c $cpu $verbose $ulp_file > $lst_file

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
    local cpu=$1
    local verbose
    if [ "$2" == verbose ]; then
        verbose=-v
        echo -e "Testing disassembling a manual byte sequence in VERBOSE mode"
    else
        echo -e "Testing disassembling a manual byte sequence in NORMAL mode"
    fi

    if [ "$cpu" == "esp32s2" ]; then
        sequence="e1af 8c74 8101 0068 2705 cc19 0005 681d 0000 00a0 0000 0078"
    else
        sequence="e1af 8c72 0100 0068 2705 cc19 0005 681d 0000 00a0 0000 0074"
    fi

    lst_file="manual_bytes.$cpu.lst"
    lst_file_fixture=fixtures/manual_bytes${verbose}.$cpu.lst
    echo -e "\tDisassembling manual byte sequence using micropython-esp32-ulp disassembler ($cpu)"
    micropython -m tools.disassemble -c $cpu $verbose -m $sequence> $lst_file

    if ! diff $lst_file_fixture $lst_file 1>/dev/null; then
        echo -e "\tDisassembled output differs from expected output!"
        echo ""
        echo "Disassembly test failed for manual byte sequence"
        echo "Diff of disassembly: expected vs actual"
        diff -u $lst_file_fixture $lst_file
    fi
}

# esp32
echo "Testing for CPU: esp32"
test_disassembling_a_file esp32
test_disassembling_a_file esp32 verbose

test_disassembling_a_manual_sequence esp32
test_disassembling_a_manual_sequence esp32 verbose

echo ""

# esp32s2
echo "Testing for CPU: esp32s2"
test_disassembling_a_file esp32s2
test_disassembling_a_file esp32s2 verbose

test_disassembling_a_manual_sequence esp32s2
test_disassembling_a_manual_sequence esp32s2 verbose
