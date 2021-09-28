  .text
  .set const, 3
  .global const  # exporting symbol is required for binutils, not important for py-esp32-ulp

entry:
  nop

  # simple jumps
  jump entry
  jump later
  jump 0x120, EQ
  jump -288, EQ

  # jumps with labels
  jumps entry, 42, lt
  jumps entry, 42, lt
  jumps later, 42, lt
  jumps entry, 42, le
  jumps later, 42, le
  jumps entry, 42, ge
  jumps later, 42, ge
  jumps entry, 42, eq
  jumps later, 42, eq
  jumps entry, 42, gt
  jumps later, 42, gt

  # jumps with immediate offset (specified in bytes, but real instruction uses words)
  jumps 0, 42, lt
  jumps 0, 42, eq  #dual-instruction condition

  jumps 4, 42, lt
  jumps 4, 42, eq  #dual-instruction condition
  jumps 8, 42, lt
  jumps 32, 42, lt

  jumps -4, 42, lt
  jumps -4, 42, eq  #dual-instruction condition
  jumps -8, 42, lt
  jumps -32, 42, lt

  # jumps with immediate offset from absolute symbol
  jumps const, 42, lt

  # jumpr with labels
  jumpr entry, 42, lt
  jumpr later, 42, lt
  jumpr entry, 42, ge
  jumpr later, 42, ge
  jumpr entry, 42, le
  jumpr later, 42, le
  jumpr entry, 42, gt
  jumpr later, 42, gt
  jumpr entry, 42, eq
  jumpr later, 42, eq

  # jumpr with immediate offset (specified in bytes, but real instruction uses words)
  jumpr 0, 42, lt
  jumpr 0, 42, eq  #dual-instruction condition

  jumpr 4, 42, lt
  jumpr 4, 42, eq  #dual-instruction condition
  jumpr 8, 42, lt
  jumpr 32, 42, lt

  jumpr -4, 42, lt
  jumpr -4, 42, eq  #dual-instruction condition
  jumpr -8, 42, lt
  jumpr -32, 42, lt

  # jumps with immediate offset from absolute symbol
  jumpr const, 42, lt

  nop
  nop
  nop
later:
