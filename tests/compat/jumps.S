  .text

entry:
  nop

  jumps entry, 42, lt
  jumps entry, 42, lt
  jumps later, 42, lt
  jumps entry, 42, le
  jumps later, 42, le
  jumps entry, 42, ge
  jumps later, 42, ge
  jumps entry, 42, eq
  jumps later, 42, eq

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

  nop
  nop
  nop
later:
