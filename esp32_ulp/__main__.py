import sys

from .assemble import Assembler
from .link import make_binary


def src_to_binary(src):
    assembler = Assembler()
    assembler.assemble(src)
    assembler.dump()
    text, data, bss_len = assembler.fetch()
    return make_binary(text, data, bss_len)


def main(fn):
    with open(fn) as f:
        src = f.read()

    binary = src_to_binary(src)

    if fn.endswith('.s') or fn.endswith('.S'):
        fn = fn[:-2]
    with open(fn + '.ulp', 'wb') as f:
        f.write(binary)


main(sys.argv[1])

