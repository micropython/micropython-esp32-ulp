#!/bin/bash
#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

# export PYTHONPATH=.:$PYTHONPATH

set -e

calc_file_hash() {
    local filename=$1

    shasum < $1 | cut -d' ' -f1
}

make_log_dir() {
   mkdir -p log
}

fetch_esp_idf() {
    [ -d esp-idf ] && return

    echo "Fetching esp-idf"
    log_file=log/fetch-esp-idf.log
    git clone --depth 1 \
        https://github.com/espressif/esp-idf.git 1>$log_file 2>&1
}

run_tests_for_cpu() {
    local cpu=$1
    echo "Testing for CPU: $cpu"

    for src_file in $(ls -1 compat/*.S fixtures/*.S); do
        src_name="${src_file%.S}"

        # files with a cpu encoded into their name are only run for that cpu
        if [[ $src_file =~ \.esp32\. && $cpu != esp32 ]] || [[ $src_file =~ \.esp32s2?\. && $cpu != esp32s2 ]]; then
            continue
        fi
        echo "Testing $src_file"
        echo -e "\tBuilding using micropython-esp32-ulp ($cpu)"
        ulp_file="${src_name}.ulp"
        log_file="${src_name}.log"
        micropython -m esp32_ulp -c $cpu $src_file 1>$log_file   # generates $ulp_file

        pre_file="${src_name}.pre"
        obj_file="${src_name}.o"
        elf_file="${src_name}.elf"
        bin_file="${src_name}.bin"

        echo -e "\tBuilding using binutils ($cpu)"
        gcc -I esp-idf/components/soc/$cpu/include -I esp-idf/components/esp_common/include \
            -x assembler-with-cpp \
            -E -o ${pre_file} $src_file
        esp32ulp-elf-as --mcpu=$cpu -o $obj_file ${pre_file}
        esp32ulp-elf-ld -T esp32.ulp.ld -o $elf_file $obj_file
        esp32ulp-elf-objcopy -O binary $elf_file $bin_file

        if ! diff $ulp_file $bin_file 1>/dev/null; then
            echo -e "\tBuild outputs differ!"
            echo ""
            echo "Compatibility test failed for $src_file"
            echo "micropython-esp32-ulp log:"
            cat $log_file
            echo "micropython-esp32-ulp output:"
            xxd $ulp_file
            echo "binutils output:"
            xxd $bin_file
            exit 1
        else
            echo -e "\tBuild outputs match (sha1: $(calc_file_hash $ulp_file))"
        fi
    done
    echo ""
}

make_log_dir
fetch_esp_idf
run_tests_for_cpu esp32
run_tests_for_cpu esp32s2
