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

  jumpr entry, 42, lt
  jumpr later, 42, lt
  jumpr entry, 42, ge
  jumpr later, 42, ge

  nop
  nop
  nop
later:
