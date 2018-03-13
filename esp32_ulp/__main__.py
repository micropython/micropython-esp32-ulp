import sys

from .assemble import Assembler


def main(fn):
    with open(fn) as f:
        lines = f.readlines()

    assembler = Assembler()
    assembler.assemble(lines)
    assembler.dump()


main(sys.argv[1])

