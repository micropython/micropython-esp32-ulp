import sys

from .util import garbage_collect

from .preprocess import preprocess
from .assemble import Assembler
from .link import make_binary
garbage_collect('after import')


def src_to_binary(src):
    assembler = Assembler()
    assembler.assemble(src, remove_comments=False)  # comments already removed by preprocessor
    garbage_collect('before symbols export')
    addrs_syms = assembler.symbols.export()
    for addr, sym in addrs_syms:
        print('%04d %s' % (addr, sym))

    text, data, bss_len = assembler.fetch()
    return make_binary(text, data, bss_len)


def main(fn):
    with open(fn) as f:
        src = f.read()

    src = preprocess(src)
    binary = src_to_binary(src)

    if fn.endswith('.s') or fn.endswith('.S'):
        fn = fn[:-2]
    with open(fn + '.ulp', 'wb') as f:
        f.write(binary)


if __name__ == '__main__':
    main(sys.argv[1])

