#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

# This file tests various fixes to the assembler,
# to ensure the binary output matches that of binutils.
# a) support for left-aligned directives (e.g. .set without preceding whitespace)
# b) a crash-fix related to data items in the .bss section
# c) support for marking labels as global
# d) support for upper case ULP opcode names
#
.set gpio, 2

.bss

counter:
.long 0

.data
var2: .int 1111

  .text
  .global entry
entry:
  MOVE R1, gpio
  WAIT 42

  # reg_rd/reg_wr with "short" and "long" address notation
  reg_rd 12, 7, 0
  reg_rd 0x3ff48000, 7, 0

  # interpret ; as statement separator - this results in 2 NOP machine instructions
  nop; nop;

  # adc supports an undocumented 4th argument, which should be entirely ignored
  # binutils-esp32ulp also ignores this argument, if present, see:
  # https://github.com/espressif/binutils-esp32ulp/blob/249ec34cc2c9574a86f3f86bbb175a863f988bcf/gas/config/esp32ulp-parse.y#L810
  adc r1, 0, 1, 100

  halt
