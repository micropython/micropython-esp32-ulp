import os
from esp32_ulp.util import split_tokens, validate_expression, file_exists

tests = []


def test(param):
    """
    the @test decorator
    """
    tests.append(param)


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
