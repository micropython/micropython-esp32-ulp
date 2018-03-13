"""
ESP32 ULP Co-Processor Assembler
"""

from . import opcodes

TEXT, DATA, BSS = 'text', 'data', 'bss'

class Assembler:

    def __init__(self):
        self.symbols = {}
        self.sections = dict(text=[], data=[])
        self.offsets = dict(text=0, data=0, bss=0)
        self.section = TEXT

    def parse_line(self, line):
        """
        parse one line of assembler into label, opcode, args

        a line looks like (label, opcode, args, comment are all optional):

        label:    opcode arg1, arg2, ...    # rest-of-line comment
        """
        line = line.split('#', 1)[0]
        line = line.split('//', 1)[0]
        line = line.rstrip()
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


    def append_section(self, value, expected_section=None):
        s = self.section
        if expected_section is not None and s is not expected_section:
            raise TypeError('only allowed in %s section' % expected_section)
        if s is BSS:
            # just increase BSS size by value
            self.offsets[s] += value
        else:
            self.sections[s].append(value)
            self.offsets[s] += len(value)

    def dump(self):
        print("Symbols:")
        for label, section_offset in sorted(self.symbols.items()):
            print(label, section_offset)
        print("%s section:" % TEXT)
        for t in self.sections[TEXT]:
            print("%08x" % int.from_bytes(t, 'little'))
        print("size: %d" % self.offsets[TEXT])
        print("%s section:" % DATA)
        for d in self.sections[DATA]:
            print("%08x" % int.from_bytes(d, 'little'))
        print("size: %d" % self.offsets[DATA])
        print("%s section:" % BSS)
        print("size: %d" % self.offsets[BSS])

    def fetch(self):
        def get_bytes(section):
            return b''.join(self.sections[section])

        return get_bytes(TEXT), get_bytes(DATA), self.offsets[BSS]

    def d_text(self):
        self.section = TEXT

    def d_data(self):
        self.section = DATA

    def d_bss(self):
        self.section = BSS

    def d_skip(self, amount, fill=None):
        s = self.section
        amount = int(amount)
        if fill is not None and s is BSS:
            raise ValueError('fill not allowed in section %s' % s)
        if s is BSS:
            self.append_section(amount)
        else:
            fill = int(fill or 0).to_bytes(1, 'little') * amount
            self.append_section(fill)

    d_space = d_skip

    def append_data(self, wordlen, args):
        data = [int(arg).to_bytes(wordlen, 'little') for arg in args]
        self.append_section(b''.join(data))

    def d_byte(self, *args):
        self.append_data(1, args)

    def d_word(self, *args):
        self.append_data(2, args)

    def d_long(self, *args):
        self.append_data(4, args)

    def assemble(self, lines):
        for label, opcode, args in self.parse(lines):
            if label is not None:
                if label in self.symbols:
                    raise Exception('label %s is already defined.' % label)
                self.symbols[label] = (self.section, self.offsets[self.section] // 4)
            if opcode is not None:
                if opcode[0] == '.':
                    # assembler directive
                    func = getattr(self, 'd_' + opcode[1:])
                    if func is not None:
                        result = func(*args)
                        if result is not None:
                            self.append_section(result)
                        continue
                else:
                    # machine instruction
                    func = getattr(opcodes, 'i_' + opcode, None)
                    if func is not None:
                        instruction = func(*args)
                        self.append_section(instruction.to_bytes(4, 'little'), TEXT)
                        continue
                raise Exception('Unknown opcode or directive: %s' % opcode)

