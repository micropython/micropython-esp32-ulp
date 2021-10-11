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

calc_file_hash() {
    local filename=$1

    shasum < $1 | cut -d' ' -f1
}

patch_test() {
    local test_name=$1
    local out_file="${test_name}.tmp"

    if [ "${test_name}" = esp32ulp_jumpr ]; then
        (
            cd binutils-esp32ulp/gas/testsuite/gas/esp32ulp/esp32
            cp ${test_name}.s ${out_file}
            echo -e "\tPatching test to work around binutils-esp32ulp .global bug"
            cat >> ${out_file} <<EOF
                .global check_jump1
EOF
        )
        return 0

    elif [ "${test_name}" = esp32ulp_ranges ]; then
        (
            cd binutils-esp32ulp/gas/testsuite/gas/esp32ulp/esp32
            # merge 2 files: https://github.com/espressif/binutils-esp32ulp/blob/249ec34/gas/testsuite/gas/esp32ulp/esp32/check_as_ld.sh#L31
            echo -e "\t${test_name} requires esp32ulp_globals. Merging both files into ${out_file}"
            cat esp32ulp_globals.s ${test_name}.s > ${out_file}
            echo -e "\tPatching test to work around binutils-esp32ulp .global bug"
            cat >> ${out_file} <<EOF
                .global min_add
                .global min_jump1
                .global max_jump1
                .global min_jumpr1
                .global max_jumpr1
EOF
        )
        return 0
    fi

    return 1  # nothing was patched
}

make_log_dir
fetch_esp_idf
fetch_ulptool_examples
fetch_binutils_esp32ulp_examples
build_defines_db $1

for src_file in ulptool/src/ulp_examples/*/*.s binutils-esp32ulp/gas/testsuite/gas/esp32ulp/esp32/*.s; do

    src_name="${src_file%.s}"
    src_dir="${src_name%/*}"

    echo "Testing $src_file"

    test_name="${src_name##*/}"

    # for now, skip files that contain unsupported things (macros)
    for I in i2c i2c_dev stack i2c_wr test1 test_jumpr test_macro; do
        if [ "${test_name}" = "$I" ]; then
            echo -e "\tSkipping... not yet supported"
            continue 2
        fi
    done

    # BEGIN: work around known issues with binutils-esp32ulp
    ulp_file="${src_name}.ulp"

    if patch_test ${test_name}; then
        # switch to the patched file instead of original one
        src_file="${src_dir}/${test_name}.tmp"
        src_name="${src_file%.tmp}"
        ulp_file="${src_name}.tmp.ulp"  # when extension is not .s, py-esp32-ulp doesn't remove original extension
    fi
    # END: work around known issues with binutils-esp32ulp

    echo -e "\tBuilding using py-esp32-ulp"
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
        echo -e "\tBuild outputs match (sha1: $(calc_file_hash $ulp_file))"
    fi
done
