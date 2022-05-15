# common example of real world code using expressions
  .set adc_channel, 6

  .set adc_oversampling_factor_log, 2
  .set adc_oversampling_factor, (1 << adc_oversampling_factor_log)

.data

result:
  .long 0

  .text
  .global entry
entry:
  move r0, 0
  stage_rst

measure:
  adc r1, 0, adc_channel + 1
  add r0, r0, r1

  stage_inc 1
  jumps measure, adc_oversampling_factor, lt

  rsh r0, r0, adc_oversampling_factor_log

  move r3, result
  st r0, r3, 0

exit:
  halt


# ---
# test that expressions evaluate correctly for all supported operators
# (these statements do not mean anything other than testing the operations)
  move r3, 1+2
  move r3, 3-5
  move r3, -5
  move r3, 2*3
  move r3, 4/2
  move r3, 4 % 3
  move r3, 0xff << 2
  move r3, 0xff >> 1
  move r3, (0xabcdef | 0xff) & 0xff
  move r3, 0x1234 & ~2
  move r3, 42|4&0xf  # 46 (4&0xf is evaluated first)
  move r3, (42|4)&0xf  # 14 (42|4 is evaluated first)

# ---
# test that expressions accept hex characters in either upper or lower case
  move r3, 0xaa - 1
  move r3, 0xBB - 1
  move r3, 0xCc - 1
  move r3, 0Xdd - 1
  move r3, 0XEF - 1
