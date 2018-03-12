# comment-only line

start:      ld r0, r1, 0    # a comment!
            st r0, r1, 0
            add r0, r1, r2
            add r0, r1, 42
            sub r0, r1, r2
            sub r0, r1, 42
            #and r0, r1, r2
            #and r0, r1, 42
            #or r0, r1, r2
            #or r0, r1, 42
            lsh r0, r1, r2
            lsh r0, r1, 42
            rsh r0, r1, r2
            rsh r0, r1, 42
            move r0, r1
            move r0, 42

            # jumping to labels not supported yet
            bl -1, 0
            bge 1, 0
            bxi 0

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
end:

