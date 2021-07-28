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

  .text
  .global entry
entry:
  MOVE R1, gpio
  WAIT 42

  # reg_rd/reg_wr with "short" and "long" address notation
  reg_rd 12, 7, 0
  reg_rd 0x3ff48000, 7, 0

  halt
