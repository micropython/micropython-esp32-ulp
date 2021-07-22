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
  halt
