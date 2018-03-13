#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

for file in opcodes assemble link ; do
    echo testing $file...
    micropython $file.py
done

for src_file in $(ls -1 compat/*.S); do
    src_name="${src_file%.S}"
    
    echo "Building $src_file using py-esp32-ulp"
    ulp_file="${src_name}.ulp"
    micropython -m esp32_ulp $src_file    # generates $ulp_file

    obj_file="${src_name}.o"
    elf_file="${src_name}.elf"
    bin_file="${src_name}.bin"

    echo "Building $src_file using binutils"
    esp32ulp-elf-as -o $obj_file $src_file
    esp32ulp-elf-ld -T esp32.ulp.ld -o $elf_file $obj_file
    esp32ulp-elf-objcopy -O binary $elf_file $bin_file

    if ! diff $ulp_file $bin_file; then
        echo "Compatibility test failed for $src_file"
        echo "py-esp32-ulp output:"
        hexdump $ulp_file
        echo "binutils output:"
        hexdump $bin_file
        exit 1
    else
        echo "Build outputs match for $src_file"
    fi
done
