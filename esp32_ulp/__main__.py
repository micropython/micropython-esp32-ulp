import sys

from .assemble import Assembler


def main(fn):
    with open(fn) as f:
        lines = f.readlines()

    assembler = Assembler()
    symbols, code = assembler.assemble(lines)

    print('Symbols:')
    for name, value in sorted(symbols.items()):
        print(name, ':', value)

    print('Code:')
    for ins in code:
        print(hex(ins))


main(sys.argv[1])

