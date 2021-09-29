#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

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

fetch_ulptool_examples() {
    [ -d ulptool ] && return

    echo "Fetching ulptool examples"
    log_file=log/fetch-ulptool.log
    git clone --depth 1 \
        https://github.com/duff2013/ulptool 1>$log_file 2>&1
}

fetch_binutils_esp32ulp_examples() {
    [ -d binutils-esp32ulp ] && return

    echo "Fetching binutils-esp32ulp examples"
    log_file=log/fetch-binutils.log
    git clone --depth 1 \
        https://github.com/espressif/binutils-esp32ulp.git 1>$log_file 2>&1
}

build_defines_db() {
    local defines_db=defines.db

    if [ "$1" = "-r" ] && [ -s "${defines_db}" ]; then
        # reuse existing defines.db
        return
    fi

    echo "Building defines DB from include files"
    log_file=log/build_defines_db.log
    rm -f "${defines_db}"
    micropython -m esp32_ulp.parse_to_db \
        esp-idf/components/soc/esp32/include/soc/*.h \
        esp-idf/components/esp_common/include/*.h 1>$log_file
}

make_log_dir
fetch_esp_idf
fetch_ulptool_examples
fetch_binutils_esp32ulp_examples
build_defines_db $1

for src_file in ulptool/src/ulp_examples/*/*.s binutils-esp32ulp/gas/testsuite/gas/esp32ulp/esp32/*.s; do

    src_name="${src_file%.s}"

    echo "Testing $src_file"

    test_name="${src_name##*/}"

    # for now, skip files that contain known bugs in esp32_ulp (essentially a todo list of what to fix)
    for I in esp32ulp_jumpr esp32ulp_ranges; do
        if [ "${test_name}" = "$I" ]; then
            # these are old bugs, and not related to the RTC macro handling functionality
            # they will still be great to fix over time
            echo -e "\tSkipping... known bugs in esp32_ulp"
            continue 2
        fi
    done

    # for now, skip files that contain unsupported things (macros)
    for I in i2c i2c_dev stack i2c_wr test1 test_jumpr test_macro; do
        if [ "${test_name}" = "$I" ]; then
            echo -e "\tSkipping... not yet supported"
            continue 2
        fi
    done

    echo -e "\tBuilding using py-esp32-ulp"
    ulp_file="${src_name}.ulp"
    log_file="${src_name}.log"
    micropython -m esp32_ulp $src_file 1>$log_file   # generates $ulp_file

    pre_file="${src_name}.pre"
    obj_file="${src_name}.o"
    elf_file="${src_name}.elf"
    bin_file="${src_name}.bin"

    echo -e "\tBuilding using binutils"
    gcc -I esp-idf/components/soc/esp32/include -I esp-idf/components/esp_common/include \
        -x assembler-with-cpp \
        -E -o ${pre_file} $src_file
    esp32ulp-elf-as -o $obj_file ${pre_file}
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
