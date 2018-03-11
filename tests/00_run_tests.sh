# export PYTHONPATH=.:$PYTHONPATH

for file in opcodes assemble link ; do
    echo testing $file...
    micropython $file.py
done

