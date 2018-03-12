from esp32_ulp.assemble import parse_line, parse, assemble

src = """\
# line 1

start:  wait 42    # line 3

        # line 5
        ld r0, r1, 0
        st  r0,  r1,0    # line 7
        halt
end:
"""


def test_parse_line():
    lines = src.splitlines()
    # note: line number = index + 1
    assert parse_line(lines[0]) == None
    assert parse_line(lines[1]) == None
    assert parse_line(lines[2]) == ('start', 'wait', ('42', ))
    assert parse_line(lines[3]) == None
    assert parse_line(lines[4]) == None
    assert parse_line(lines[5]) == (None, 'ld', ('r0', 'r1', '0', ))
    assert parse_line(lines[6]) == (None, 'st', ('r0', 'r1', '0', ))
    assert parse_line(lines[7]) == (None, 'halt', ())
    assert parse_line(lines[8]) == ('end', None, ())


def test_parse():
    lines = src.splitlines()
    result = parse(lines)
    assert None not in result


def test_assemble():
    lines = src.splitlines()
    symbols, code = assemble(lines)
    assert {'start', 'end'} < set(symbols)
    assert symbols['start'] == 0
    assert symbols['end'] == 4
    assert len(code) == 4


test_parse_line()
test_parse()
test_assemble()

