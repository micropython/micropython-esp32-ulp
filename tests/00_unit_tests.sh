#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

LIST=${1:-opcodes opcodes_s2 assemble link util preprocess definesdb disassemble}

for file in $LIST; do
    echo testing $file...
    micropython $file.py
done
