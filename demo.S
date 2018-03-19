# comment-only line

            .text

textstart:  ld r0, r1, 0    # a comment!
            st r0, r1, 0    // another comment!
            add r0, r1, r2
            add r0, r1, 42
            sub r0, r1, r2
            sub r0, r1, 42
            and r0, r1, r2
            and r0, r1, 42
            or r0, r1, r2
            or r0, r1, 42
            lsh r0, r1, r2
            lsh r0, r1, 42
            rsh r0, r1, r2
            rsh r0, r1, 42
            move r0, r1
            move r0, 42
            move r0, textstart  # moves abs addr of textstart to r0
            stage_rst
            stage_inc 42
            stage_dec 23

rel_b:      jumpr -1, 42, lt
            jumpr rel_b, 42, LT
            jumpr rel_f, 23, ge
rel_f:      jumpr +1, 23, GE
            jump textstart
            jump 0, eq
            jump 0, OV
            jump r0
            jump r0, EQ
            jump r0, ov
            jumps -1, 42, lt
            jumps +1, 23, GT
            jumps 0, 0xAD, Eq

            reg_rd 0x3ff48000, 7, 0
            reg_wr 0x3ff48000, 7, 0, 42

            i2c_rd 0x10, 7, 0, 0
            i2c_wr 0x23, 0x42, 7, 0, 1

            adc r0, 0, 1

            nop
            wait 1000
            wake
            sleep 1
            halt
textend:

            .data
data0:      .skip 4, 0x23
data1:      .space 4, 0x42
data2:      .skip 4
dataw:      .word 1, 2, 3, 4
datal:      .long 1, 2, 3, 4
datab:      .byte 1, 2, 3  # test alignment / fill up of section
dataend:

            .bss
bss0:       .skip 4
bss1:       .skip 2  # test alignment / fill up of section
bssend:
