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

            rd_reg 0x3ff48000, 1, 2
            wr_reg 0x3ff48000, 1, 2, 3

            wait 1000
            wake
            sleep 1
            halt
end:

