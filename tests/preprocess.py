from esp32_ulp.preprocess import Preprocessor

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

    assert p.parse_defines("") == {}
    assert p.parse_defines("// comment") == {}
    assert p.parse_defines("  // comment") == {}
    assert p.parse_defines("  /* comment */") == {}
    assert p.parse_defines("  /* comment */ #define A 42") == {}  # #define must be the first thing on a line
    assert p.parse_defines("#define a 1") == {"a": "1"}
    assert p.parse_defines(" #define a 1") == {"a": "1"}
    assert p.parse_defines("#define a 1 2") == {"a": "1 2"}
    assert p.parse_defines("#define f(a,b) 1") == {}  # macros not supported
    assert p.parse_defines("#define f(a, b) 1") == {}  # macros not supported
    assert p.parse_defines("#define f (a,b) 1") == {"f": "(a,b) 1"}  # f is not a macro
    assert p.parse_defines("#define f (a, b) 1") == {"f": "(a, b) 1"}  # f is not a macro
    assert p.parse_defines("#define RTC_ADDR       0x12345    // start of range") == {"RTC_ADDR": "0x12345"}


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


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
