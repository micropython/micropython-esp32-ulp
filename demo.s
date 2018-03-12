# comment-only line

start:      ld r0, r0, 0    # a comment!
            st r0, r0, 0
            addr r0, r1, r2
            addi r0, r1, 42
            movr r0, r1
            movi r0, 42
            bl -1, 0
            bge 1, 0
            bxi start

            reg_rd 0x3ff48000, 7, 0
            reg_wr 0x3ff48000, 7, 0, 42

            i2c_rd 0x10, 7, 0, 0
            i2c_wr 0x23, 0x42, 7, 0, 1

            adc r0, 0, 1

            wait 1000
            wake
            sleep 1
            halt
end:

