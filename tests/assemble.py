from esp32_ulp.assemble import Assembler, TEXT, DATA, BSS, REL, ABS

src = """\

start:  wait 42
        ld r0, r1, 0
        st  r0,  r1,0
        halt
end:
"""


def test_parse_line():
    a = Assembler()
    lines = src.splitlines()
    # note: line number = index + 1
    assert a.parse_line(lines[0]) == None
    assert a.parse_line(lines[1]) == ('start', 'wait', ('42', ))
    assert a.parse_line(lines[2]) == (None, 'ld', ('r0', 'r1', '0', ))
    assert a.parse_line(lines[3]) == (None, 'st', ('r0', 'r1', '0', ))
    assert a.parse_line(lines[4]) == (None, 'halt', ())
    assert a.parse_line(lines[5]) == ('end', None, ())


def test_parse():
    a = Assembler()
    result = a.parse(src)
    assert None not in result


def test_assemble():
    a = Assembler()
    a.assemble(src)
    assert a.symbols.has_sym('start')
    assert a.symbols.has_sym('end')
    assert a.symbols.get_sym('start') == (REL, TEXT, 0)
    assert a.symbols.get_sym('end') == (REL, TEXT, 4)
    assert len(b''.join(a.sections[TEXT])) == 16  # 4 instructions * 4B
    assert len(a.sections[DATA]) == 0
    assert a.offsets[BSS] == 0


test_parse_line()
test_parse()
test_assemble()

