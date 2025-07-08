#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

import os
from esp32_ulp.util import split_tokens, validate_expression, parse_int, file_exists

tests = []


def test(param):
    """
    the @test decorator
    """
    tests.append(param)


def assert_raises(exception, func, *args, message=None):
    try:
        func(*args)
    except exception as e:
        raised = True
        actual_message = e.args[0]
    else:
        raised = False
    assert raised
    if message:
        assert actual_message == message, '%s == %s' % (actual_message, message)


@test
def test_split_tokens():
    assert split_tokens("") == []
    assert split_tokens("t") == ['t']
    assert split_tokens("test") == ['test']
    assert split_tokens("t t") == ['t', ' ', 't']
    assert split_tokens("t,t") == ['t', ',', 't']
    assert split_tokens("test(arg)") == ['test', '(', 'arg', ')']
    assert split_tokens("test(arg,arg2)") == ['test', '(', 'arg', ',', 'arg2', ')']
    assert split_tokens("test(arg,arg2)") == ['test', '(', 'arg', ',', 'arg2', ')']
    assert split_tokens("  test(  arg,  arg2)") == ['  ', 'test', '(', '  ', 'arg', ',', '  ', 'arg2', ')']
    assert split_tokens("  test(  arg )  ") == ['  ', 'test', '(', '  ', 'arg', ' ', ')', '  ']
    assert split_tokens("\t  test  \t  ") == ['\t  ', 'test', "  \t  "]
    assert split_tokens("test\nrow2") == ['test', "\n", "row2"]

    # split_token does not support comments. should generally only be used after comments are already stripped
    assert split_tokens("test(arg /*comment*/)") == ['test', '(', 'arg', ' ', '/', '*', 'comment', '*', '/', ')']
    assert split_tokens("#test") == ['#', 'test']


@test
def test_validate_expression():
    assert validate_expression('') is True
    assert validate_expression('1') is True
    assert validate_expression('1+1') is True
    assert validate_expression('(1+1)') is True
    assert validate_expression('(1+1)*2') is True
    assert validate_expression('(1 + 1)') is True
    assert validate_expression('10 % 2') is True
    assert validate_expression('0x100 << 2') is True
    assert validate_expression('0x100 & ~2') is True
    assert validate_expression('0xabcdef') is True
    assert validate_expression('0x123def') is True
    assert validate_expression('0xABC') is True
    assert validate_expression('0xaBc') is True
    assert validate_expression('0Xabc') is True
    assert validate_expression('0X123ABC') is True
    assert validate_expression('2*3+4/5&6|7') is True
    assert validate_expression('(((((1+1) * 2') is True  # valid characters, even if expression is not valid

    assert validate_expression(':') is False
    assert validate_expression('_') is False
    assert validate_expression('=') is False
    assert validate_expression('.') is False
    assert validate_expression('!') is False
    assert validate_expression('123 ^ 4') is False  # operator not supported for now
    assert validate_expression('evil()') is False
    assert validate_expression('def cafe()') is False  # valid hex digits, but potentially dangerous code
    assert validate_expression('def CAFE()') is False


@test
def test_parse_int():
    # decimal
    assert parse_int("0") == 0, "0 == 0"
    assert parse_int("5") == 5, "5 == 5"
    assert parse_int("-0") == 0, "-0 == 0"
    assert parse_int("-5") == -5, "-5 == -5"
    # hex
    assert parse_int("0x5") == 5, "0x5 == 5"
    assert parse_int("0x5a") == 90, "0x5a == 90"
    assert parse_int("-0x5a") == -90, "-0x5a == -90"
    # binary
    assert parse_int("0b1001") == 9, "0b1001 == 9"
    assert parse_int("-0b1001") == -9, "-0b1001 == 9"
    # octal
    assert parse_int("07") == 7, "07 == 7"
    assert parse_int("0100") == 64, "0100 == 64"
    assert parse_int("0o210") == 136, "0o210 == 136"
    assert parse_int("00000010") == 8, "00000010 == 8"
    assert parse_int("-07") == -7, "-07 == -7"
    assert parse_int("-0100") == -64, "-0100 == -64"
    assert parse_int("-0o210") == -136, "-0o210 == -136"
    assert parse_int("-00000010") == -8, "-00000010 == -8"
    # negative cases
    assert_raises(ValueError, parse_int, '0b123', message="invalid syntax for integer with base 2: '123'")
    assert_raises(ValueError, parse_int, '0900', message="invalid syntax for integer with base 8: '0900'")
    assert_raises(ValueError, parse_int, '0o900', message="invalid syntax for integer with base 8: '900'")
    assert_raises(ValueError, parse_int, '0xg', message="invalid syntax for integer with base 16: 'g'")


@test
def test_file_exists():
    testfile = '.testfile'
    with open(testfile, 'w') as f:
        f.write('contents')

    assert file_exists(testfile)

    os.remove(testfile)

    assert not file_exists(testfile)


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
