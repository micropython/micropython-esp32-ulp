"""
ESP32 ULP Co-Processor Assembler
"""

from . import opcodes

class Assembler:
    def __init__(self):
        self.symbols = {}
        self.code = []
        self.addr = 0

    def parse_line(self, line):
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


    def parse(self, lines):
        parsed = [self.parse_line(line) for line in lines]
        return [p for p in parsed if p is not None]


    def assemble(self, lines):
        for label, opcode, args in self.parse(lines):
            if label is not None:
                if label in self.symbols:
                    raise Exception('label %s is already defined.' % label)
                self.symbols[label] = self.addr
            if opcode is not None:
                func = getattr(opcodes, 'i_' + opcode, None)
                if func is None:
                    raise Exception('Unknown opcode: %s' % opcode)
                instruction = func(*args)
                self.code.append(instruction)
                self.addr += 1
        return self.symbols, self.code

