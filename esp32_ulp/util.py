#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

DEBUG = False

import gc
import os

NORMAL, WHITESPACE = 0, 1


def garbage_collect(msg, verbose=DEBUG):
    free_before = gc.mem_free()
    gc.collect()
    free_after = gc.mem_free()
    if verbose:
        print("%s: %d --gc--> %d bytes free" % (msg, free_before, free_after))


def split_tokens(line):
    buf = ""
    tokens = []
    state = NORMAL
    for c in line:
        if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_":
            if state != NORMAL:
                if len(buf) > 0:
                    tokens.append(buf)
                    buf = ""
                state = NORMAL
            buf += c
        elif c in " \t":
            if state != WHITESPACE:
                if len(buf) > 0:
                    tokens.append(buf)
                    buf = ""
                state = WHITESPACE
            buf += c
        else:
            if len(buf) > 0:
                tokens.append(buf)
                buf = ""
            tokens.append(c)

    if len(buf) > 0:
        tokens.append(buf)

    return tokens


def validate_expression(param):
    for token in split_tokens(param):
        state = 0
        for c in token:
            if c not in ' \t+-*/%()<>&|~xX0123456789abcdefABCDEF':
                return False

            # the following allows hex digits a-f after 0x but not otherwise
            if state == 0:
                if c in 'abcdefABCDEF':
                    return False
                if c == '0':
                    state = 1
                continue

            if state == 1:
                state = 2 if c in 'xX' else 0
                continue

            if state == 2:
                if c not in '0123456789abcdefABCDEF':
                    state = 0
    return True


def parse_int(literal):
    """
    GNU as compatible parsing of string literals into integers
    Specifically, GNU as treats literals starting with 0 as octal
    All other literals are correctly parsed by Python
    See: https://sourceware.org/binutils/docs/as/Integers.html
    """
    if len(literal) >= 2 and (literal.startswith("0") or literal.startswith("-0")) and literal.lstrip("-0").isdigit():
        return int(literal, 8)
    return int(literal, 0)


def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        pass
    return False
