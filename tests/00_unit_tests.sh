#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

for file in opcodes assemble link util preprocess definesdb disassemble; do
    echo testing $file...
    micropython $file.py
done
