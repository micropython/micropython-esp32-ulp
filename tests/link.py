#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

from esp32_ulp.link import make_binary


def test_make_binary():
    text = b'\x12\x34\x56\x78'
    data = b'\x11\x22\x33\x44'
    bss_size = 40
    bin = make_binary(text, data, bss_size)
    assert len(bin) == 12 + len(text) + len(data)
    assert bin.startswith(b'\x75\x6c\x70\x00')  # magic, LE
    assert bin.endswith(text+data)


test_make_binary()

