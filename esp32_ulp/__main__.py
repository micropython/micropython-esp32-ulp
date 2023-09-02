import sys
from . import assemble_file


def main(fn, cpu):
    assemble_file(fn, cpu)


if __name__ == '__main__':
    cpu = 'esp32'
    filename = sys.argv[1]
    if len(sys.argv) > 3:
        if sys.argv[1] in ('-c', '--mcpu'):
            cpu = sys.argv[2].lower()
            if cpu not in ('esp32', 'esp32s2'):
                raise ValueError('Invalid cpu')
            filename = sys.argv[3]
    main(filename, cpu)

