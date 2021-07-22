#!/bin/bash

# export PYTHONPATH=.:$PYTHONPATH

set -e

for file in opcodes assemble link util; do
    echo testing $file...
    micropython $file.py
done
