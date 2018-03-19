#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

for src_file in $(ls -1 compat/*.S); do
    src_name="${src_file%.S}"
    
    echo "Testing $src_file"
    echo -e "\tBuilding using py-esp32-ulp"
    ulp_file="${src_name}.ulp"
    log_file="${src_name}.log"
    micropython -m esp32_ulp $src_file 1>$log_file   # generates $ulp_file

    obj_file="${src_name}.o"
    elf_file="${src_name}.elf"
    bin_file="${src_name}.bin"

    echo -e "\tBuilding using binutils"
    esp32ulp-elf-as -o $obj_file $src_file
    esp32ulp-elf-ld -T esp32.ulp.ld -o $elf_file $obj_file
    esp32ulp-elf-objcopy -O binary $elf_file $bin_file

    if ! diff $ulp_file $bin_file 1>/dev/null; then
        echo -e "\tBuild outputs differ!"
        echo ""
        echo "Compatibility test failed for $src_file"
        echo "py-esp32-ulp log:"
        cat $log_file
        echo "py-esp32-ulp output:"
        xxd $ulp_file
        echo "binutils output:"
        xxd $bin_file
        exit 1
    else
        echo -e "\tBuild outputs match"
    fi
done
