# export PYTHONPATH=.:$PYTHONPATH

for file in opcodes assemble ; do
    echo testing $file...
    micropython $file.py
done

