import sys

from .assemble import assemble


def main(fn):
    with open(fn) as f:
        lines = f.readlines()

    symbols, code = assemble(lines)

    print('Symbols:')
    for name, value in sorted(symbols.items()):
        print(name, ':', value)

    print('Code:')
    for ins in code:
        print(hex(ins))


main(sys.argv[1])

