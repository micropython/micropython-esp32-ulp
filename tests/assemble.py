from esp32_ulp.assemble import Assembler, TEXT, DATA, BSS, REL, ABS
from esp32_ulp.assemble import SymbolTable
from esp32_ulp.nocomment import remove_comments

src = """\
        .set const, 123
.set const_left, 976

start:  wait 42
        ld r0, r1, 0
        st  r0,  r1,0
        halt
end:
.data
"""

src_bss = """\
  .bss

label:
  .long 0
"""


src_global = """\

  .global counter
counter:
  .long 0

internal:
  .long 0

  .text
  .global entry
entry:
  wait 42
  halt
"""


def test_parse_line():
    a = Assembler()
    lines = iter(src.splitlines())
    assert a.parse_line(next(lines)) == (None, '.set', ('const', '123', ))
    assert a.parse_line(next(lines)) == (None, '.set', ('const_left', '976', ))
    assert a.parse_line(next(lines)) == None
    assert a.parse_line(next(lines)) == ('start', 'wait', ('42', ))
    assert a.parse_line(next(lines)) == (None, 'ld', ('r0', 'r1', '0', ))
    assert a.parse_line(next(lines)) == (None, 'st', ('r0', 'r1', '0', ))
    assert a.parse_line(next(lines)) == (None, 'halt', ())
    assert a.parse_line(next(lines)) == ('end', None, ())
    assert a.parse_line(next(lines)) == (None, '.data', ())  # test left-aligned directive is not treated as label


def test_parse():
    a = Assembler()
    lines = remove_comments(src)
    result = a.parse(lines)
    assert None not in result


def test_assemble():
    a = Assembler()
    a.assemble(src)
    assert a.symbols.has_sym('const')
    assert a.symbols.has_sym('const_left')
    assert a.symbols.has_sym('start')
    assert a.symbols.has_sym('end')
    assert a.symbols.get_sym('const') == (ABS, None, 123)
    assert a.symbols.get_sym('const_left') == (ABS, None, 976)
    assert a.symbols.get_sym('start') == (REL, TEXT, 0)
    assert a.symbols.get_sym('end') == (REL, TEXT, 4)
    assert len(b''.join(a.sections[TEXT])) == 16  # 4 instructions * 4B
    assert len(a.sections[DATA]) == 0
    assert a.offsets[BSS] == 0


def test_assemble_bss():
    a = Assembler()
    try:
        a.assemble(src_bss)
    except TypeError:
        raised = True
    else:
        raised = False
    assert not raised
    assert a.offsets[BSS] == 4  # 1 word * 4B


def test_assemble_bss_with_value():
    lines = """\
.bss
    .long 3  #non-zero value not allowed in bss section
"""

    a = Assembler()
    try:
        a.assemble(lines)
    except ValueError as e:
        if str(e) != "attempt to store non-zero value in section .bss":
            raise  # re-raise failures we didn't expect
        raised = True
    else:
        raised = False

    assert raised


def test_assemble_global():
    a = Assembler()
    a.assemble(src_global)
    assert a.symbols.has_sym('counter')
    assert a.symbols.has_sym('internal')
    assert a.symbols.has_sym('entry')

    exported_symbols = a.symbols.export()
    assert exported_symbols == [(0, 'counter'), (2, 'entry')]  # internal not exported

    exported_symbols = a.symbols.export(True)  # include non-global symbols
    assert exported_symbols == [(0, 'counter'), (1, 'internal'), (2, 'entry')]


def test_assemble_uppercase_opcode():
    a = Assembler()
    try:
        a.assemble("  WAIT 42")
    except ValueError as e:
        if str(e) != "Unknown opcode or directive: WAIT":
            # re-raise failures we didn't expect
            raise
        raised = True
    else:
        raised = False
    assert not raised


def test_assemble_evalulate_expressions():
    src_w_expr = """\
    .set shft, 2
    .set loops, (1 << shft)

entry:
    move r0, 1+1
    move r1, loops
    move r2, (shft + 10) * 2
    move r3, entry << 2
"""
    a = Assembler()
    a.assemble(src_w_expr)

    assert a.symbols.has_sym('shft')
    assert a.symbols.has_sym('loops')
    assert a.symbols.has_sym('entry')
    assert a.symbols.get_sym('shft') == (ABS, None, 2)
    assert a.symbols.get_sym('loops') == (ABS, None, 4)
    assert a.symbols.get_sym('entry') == (REL, TEXT, 0)


def test_assemble_optional_comment_removal():
    line = " move r1, 123  # comment"

    a = Assembler()

    # first assemble as normal (comments will be removed by default)
    a.assemble(line)

    # now assemble with comment removal disabled
    try:
        a.assemble(line, remove_comments=False)
    except ValueError as e:
        raised = True
    else:
        raised = False
    assert raised


def test_symbols():
    st = SymbolTable({}, {}, {})
    for entry in [
        ('rel_t4', REL, TEXT, 4),
        ('abs_t4', ABS, TEXT, 4),
        ('rel_d4', REL, DATA, 4),
        ('abs_d4', ABS, DATA, 4),
        ('const', ABS, None, 123),
    ]:
        st.set_sym(*entry)
    # PASS 1 ========================================================
    st.set_pass(1)
    assert st.has_sym('abs_t4')
    assert st.get_sym('abs_t4') == (ABS, TEXT, 4)
    assert not st.has_sym('notexist')
    assert st.get_sym('notexist') == (REL, TEXT, 0)  # pass1 -> dummy
    assert st.resolve_absolute('abs_t4') == 4
    assert st.resolve_absolute('abs_d4') == 4
    assert st.resolve_absolute('rel_t4') == 4
    assert st.resolve_absolute('rel_d4') == 4
    assert st.resolve_absolute('const') == 123
    st.set_from(TEXT, 8)
    assert st.resolve_relative('abs_t4') == -4
    assert st.resolve_relative('abs_d4') == -4
    assert st.resolve_relative('rel_t4') == -4
    assert st.resolve_relative('rel_d4') == -4
    assert st.resolve_absolute('const') == 123
    # PASS 2 ========================================================
    st.set_bases({TEXT: 100, DATA: 200})
    st.set_pass(2)
    assert st.has_sym('abs_t4')
    assert st.get_sym('abs_t4') == (ABS, TEXT, 4)
    assert not st.has_sym('notexist')
    try:
        st.get_sym('notexist')  # pass2 -> raises
    except KeyError:
        raised = True
    else:
        raised = False
    assert raised
    assert st.resolve_absolute('abs_t4') == 4
    assert st.resolve_absolute('abs_d4') == 4
    assert st.resolve_absolute('rel_t4') == 100 + 4
    assert st.resolve_absolute('rel_d4') == 200 + 4
    assert st.resolve_absolute('const') == 123
    st.set_from(TEXT, 8)
    assert st.resolve_relative('abs_t4') == 4 - 108
    assert st.resolve_relative('abs_d4') == 4 - 108
    assert st.resolve_relative('rel_t4') == 104 - 108
    assert st.resolve_relative('rel_d4') == 204 - 108
    assert st.resolve_absolute('const') == 123


test_parse_line()
test_parse()
test_assemble()
test_assemble_bss()
test_assemble_bss_with_value()
test_assemble_global()
test_assemble_uppercase_opcode()
test_assemble_evalulate_expressions()
test_assemble_optional_comment_removal()
test_symbols()
