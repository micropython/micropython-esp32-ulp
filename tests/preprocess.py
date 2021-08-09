import os

from esp32_ulp.preprocess import Preprocessor
from esp32_ulp.definesdb import DefinesDB, DBNAME
from esp32_ulp.util import file_exists

tests = []


def test(param):
    tests.append(param)


@test
def test_replace_defines_should_return_empty_line_given_empty_string():
    p = Preprocessor()

    assert p.preprocess("") == ""


@test
def replace_defines_should_return_remove_comments():
    p = Preprocessor()

    line = "// some comment"
    expected = ""
    assert p.preprocess(line) == expected


@test
def test_parse_defines():
    p = Preprocessor()

    assert p.parse_define_line("") == {}
    assert p.parse_define_line("// comment") == {}
    assert p.parse_define_line("  // comment") == {}
    assert p.parse_define_line("  /* comment */") == {}
    assert p.parse_define_line("  /* comment */ #define A 42") == {}  # #define must be the first thing on a line
    assert p.parse_define_line("#define a 1") == {"a": "1"}
    assert p.parse_define_line(" #define a 1") == {"a": "1"}
    assert p.parse_define_line("#define a 1 2") == {"a": "1 2"}
    assert p.parse_define_line("#define f(a,b) 1") == {}  # macros not supported
    assert p.parse_define_line("#define f(a, b) 1") == {}  # macros not supported
    assert p.parse_define_line("#define f (a,b) 1") == {"f": "(a,b) 1"}  # f is not a macro
    assert p.parse_define_line("#define f (a, b) 1") == {"f": "(a, b) 1"}  # f is not a macro
    assert p.parse_define_line("#define RTC_ADDR       0x12345    // start of range") == {"RTC_ADDR": "0x12345"}


@test
def test_parse_defines_handles_multiple_input_lines():
    p = Preprocessor()

    multi_line_1 = """\
#define ID_WITH_UNDERSCORE something
#define ID2 somethingelse
"""
    assert p.parse_defines(multi_line_1) == {"ID_WITH_UNDERSCORE": "something", "ID2": "somethingelse"}


@test
def test_parse_defines_does_not_understand_comments_by_current_design():
    # comments are not understood. lines are expected to already have comments removed!
    p = Preprocessor()

    multi_line_2 = """\
#define ID_WITH_UNDERSCORE something
/*
#define ID2 somethingelse
*/
"""
    assert "ID2" in p.parse_defines(multi_line_2)


@test
def test_parse_defines_does_not_understand_line_continuations_with_backslash_by_current_design():
    p = Preprocessor()

    multi_line_3 = r"""
    #define ID_WITH_UNDERSCORE something \
           line2
    """

    assert p.parse_defines(multi_line_3) == {"ID_WITH_UNDERSCORE": "something \\"}


@test
def preprocess_should_remove_comments_and_defines_but_keep_the_lines_as_empty_lines():
    p = Preprocessor()

    lines = """\
    // copyright
    #define A 1

    move r1, r2"""

    assert p.preprocess(lines) == "\n\n\n\tmove r1, r2"


@test
def preprocess_should_replace_words_defined():
    p = Preprocessor()

    lines = """\
    #define DR_REG_RTCIO_BASE 0x3ff48400

    move r1, DR_REG_RTCIO_BASE"""

    assert "move r1, 0x3ff48400" in p.preprocess(lines)


@test
def preprocess_should_replace_words_defined_multiple_times():
    p = Preprocessor()

    lines = """\
    #define DR_REG_RTCIO_BASE 0x3ff48400

    move r1, DR_REG_RTCIO_BASE  #once
    move r2, DR_REG_RTCIO_BASE  #second time"""

    assert "move r1, 0x3ff48400" in p.preprocess(lines)
    assert "move r2, 0x3ff48400" in p.preprocess(lines)


@test
def preprocess_should_replace_all_defined_words():
    p = Preprocessor()

    lines = """\
    #define DR_REG_RTCIO_BASE 0x3ff48400
    #define SOME_OFFSET 4

    move r1, DR_REG_RTCIO_BASE
    add r2, r1, SOME_OFFSET"""

    assert "move r1, 0x3ff48400" in p.preprocess(lines)
    assert "add r2, r1, 4" in p.preprocess(lines)


@test
def preprocess_should_not_replace_substrings_within_identifiers():
    p = Preprocessor()

    # ie. if AAA is defined don't touch PREFIX_AAA_SUFFIX
    lines = """\
    #define RTCIO 4
    move r1, DR_REG_RTCIO_BASE"""

    assert "DR_REG_4_BASE" not in p.preprocess(lines)

    # ie. if A and AA are defined, don't replace AA as two A's but with AA
    lines = """\
    #define A 4
    #define AA 8
    move r1, A
    move r2, AA"""

    assert "move r1, 4" in p.preprocess(lines)
    assert "move r2, 8" in p.preprocess(lines)


@test
def preprocess_should_replace_defines_used_in_defines():
    p = Preprocessor()

    lines = """\
    #define BITS (BASE << 4)
    #define BASE 0x1234

    move r1, BITS
    move r2, BASE"""

    assert "move r1, (0x1234 << 4)" in p.preprocess(lines)


@test
def test_expand_rtc_macros():
    p = Preprocessor()

    assert p.expand_rtc_macros("") == ""
    assert p.expand_rtc_macros("abc") == "abc"
    assert p.expand_rtc_macros("WRITE_RTC_REG(1, 2, 3, 4)") == "\treg_wr 1, 2 + 3 - 1, 2, 4"
    assert p.expand_rtc_macros("READ_RTC_REG(1, 2, 3)") == "\treg_rd 1, 2 + 3 - 1, 2"
    assert p.expand_rtc_macros("WRITE_RTC_FIELD(1, 2, 3)") == "\treg_wr 1, 2 + 1 - 1, 2, 3 & 1"
    assert p.expand_rtc_macros("READ_RTC_FIELD(1, 2)") == "\treg_rd 1, 2 + 1 - 1, 2"


@test
def preprocess_should_replace_BIT_with_empty_string_unless_defined():
    # by default replace BIT with empty string (see description for why in the code)
    src = " move r1, 0x123 << BIT(24)"
    assert "move r1, 0x123 << (24)" in Preprocessor().preprocess(src)

    # but if BIT is defined, use that
    src = """\
    #define BIT 12

    move r1, BIT"""

    assert "move r1, 12" in Preprocessor().preprocess(src)


@test
def test_process_include_file():
    p = Preprocessor()

    defines = p.process_include_file('fixtures/incl.h')

    assert defines['CONST1'] == '42'
    assert defines['CONST2'] == '99'
    assert defines.get('MULTI_LINE', None) == 'abc \\'  # correct. line continuations not supported
    assert 'MACRO' not in defines


@test
def test_process_include_file_with_multiple_files():
    p = Preprocessor()

    defines = p.process_include_file('fixtures/incl.h')
    defines = p.process_include_file('fixtures/incl2.h')

    assert defines['CONST1'] == '42', "constant from incl.h"
    assert defines['CONST2'] == '123', "constant overridden by incl2.h"
    assert defines['CONST3'] == '777', "constant from incl2.h"


@test
def test_process_include_file_using_database():
    db = DefinesDB()
    db.clear()

    p = Preprocessor()
    p.use_db(db)

    p.process_include_file('fixtures/incl.h')
    p.process_include_file('fixtures/incl2.h')

    assert db['CONST1'] == '42', "constant from incl.h"
    assert db['CONST2'] == '123', "constant overridden by incl2.h"
    assert db['CONST3'] == '777', "constant from incl2.h"

    db.close()


@test
def test_process_include_file_should_not_load_database_keys_into_instance_defines_dictionary():
    db = DefinesDB()
    db.clear()

    p = Preprocessor()
    p.use_db(db)

    p.process_include_file('fixtures/incl.h')

    # a bit hackish to reference instance-internal state
    # but it's important to verify this, as we otherwise run out of memory on device
    assert 'CONST2' not in p._defines



@test
def test_preprocess_should_use_definesdb_when_provided():
    p = Preprocessor()

    content = """\
#define LOCALCONST 42

entry:
    move r1, LOCALCONST
    move r2, DBKEY
"""

    # first try without db
    result = p.preprocess(content)

    assert "move r1, 42" in result
    assert "move r2, DBKEY" in result
    assert "move r2, 99" not in result

    # now try with db
    db = DefinesDB()
    db.clear()
    db.update({'DBKEY': '99'})
    p.use_db(db)

    result = p.preprocess(content)

    assert "move r1, 42" in result
    assert "move r2, 99" in result
    assert "move r2, DBKEY" not in result


@test
def test_preprocess_should_ensure_no_definesdb_is_created_when_only_reading_from_it():
    content = """\
    #define CONST 42
    move r1, CONST"""

    # remove any existing db
    db = DefinesDB()
    db.clear()
    assert not file_exists(DBNAME)

    # now preprocess using db
    p = Preprocessor()
    p.use_db(db)

    result = p.preprocess(content)

    assert "move r1, 42" in result

    assert not file_exists(DBNAME)


@test
def test_preprocess_should_ensure_the_definesdb_is_properly_closed_after_use():
    content = """\
    #define CONST 42
    move r1, CONST"""

    # remove any existing db
    db = DefinesDB()
    db.open()
    assert db.is_open()

    # now preprocess using db
    p = Preprocessor()
    p.use_db(db)

    p.preprocess(content)

    assert not db.is_open()


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
