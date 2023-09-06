#!/bin/bash
#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

# export PYTHONPATH=.:$PYTHONPATH

set -e

LIST=${1:-opcodes opcodes_s2 assemble link util preprocess definesdb decode decode_s2}

for file in $LIST; do
    echo testing $file...
    micropython $file.py
done
