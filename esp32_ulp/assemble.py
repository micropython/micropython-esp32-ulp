"""
ESP32 ULP Co-Processor Assembler
"""

from . import opcodes


def parse_line(line):
    """
    parse one line of assembler into label, opcode, args

    a line looks like (label, opcode, args, comment are all optional):

    label:    opcode arg1, arg2, ...    # rest-of-line comment
    """
    line = line.split('#', 1)[0].rstrip()
    if not line:
        return
    has_label = line[0] not in '\t '
    if has_label:
        label_line = line.split(None, 1)
        if len(label_line) == 2:
            label, line = label_line
        else:  # 1
            label, line = label_line[0], None
        label = label.rstrip(':')
    else:
        label, line = None, line.lstrip()
    if line is None:
        opcode, args = None, ()
    else:
        opcode_args = line.split(None, 1)
        if len(opcode_args) == 2:
            opcode, args = opcode_args
            args = tuple(arg.strip() for arg in args.split(','))
        else:  # 1
            opcode, args = opcode_args[0], ()
    return label, opcode, args


def parse(lines):
    parsed = [parse_line(line) for line in lines]
    return [p for p in parsed if p is not None]


def assemble(lines):
    symbols = dict(r0=0, R0=0, r1=1, R1=1, r2=2, R2=2, r3=3, R3=3)
    code = []
    addr = 0
    for label, opcode, args in parse(lines):
        if label is not None:
            if label in symbols:
                raise Exception('label %s is already defined.' % label)
            symbols[label] = addr
        if opcode is not None:
            func = getattr(opcodes, 'i_' + opcode, None)
            if func is None:
                raise Exception('Unknown opcode: %s' % opcode)
            instruction = func(*args)
            code.append(instruction)
            addr += 1
    return symbols, code

