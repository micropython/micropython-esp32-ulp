from esp32_ulp.assemble import Assembler, TEXT, DATA, BSS

src = """\
# line 1

start:  wait 42    # line 3

        # line 5
        ld r0, r1, 0
        st  r0,  r1,0    # line 7
        halt
end:    // C style comment
"""


def test_parse_line():
    a = Assembler()
    lines = src.splitlines()
    # note: line number = index + 1
    assert a.parse_line(lines[0]) == None
    assert a.parse_line(lines[1]) == None
    assert a.parse_line(lines[2]) == ('start', 'wait', ('42', ))
    assert a.parse_line(lines[3]) == None
    assert a.parse_line(lines[4]) == None
    assert a.parse_line(lines[5]) == (None, 'ld', ('r0', 'r1', '0', ))
    assert a.parse_line(lines[6]) == (None, 'st', ('r0', 'r1', '0', ))
    assert a.parse_line(lines[7]) == (None, 'halt', ())
    assert a.parse_line(lines[8]) == ('end', None, ())


def test_parse():
    a = Assembler()
    lines = src.splitlines()
    result = a.parse(lines)
    assert None not in result


def test_assemble():
    a = Assembler()
    lines = src.splitlines()
    a.assemble(lines)
    assert {'start', 'end'} <= set(a.symbols)
    assert a.symbols['start'] == (TEXT, 0)
    assert a.symbols['end'] == (TEXT, 4)
    assert len(b''.join(a.sections[TEXT])) == 16  # 4 instructions * 4B
    assert len(a.sections[DATA]) == 0
    assert a.offsets[BSS] == 0


test_parse_line()
test_parse()
test_assemble()

