            .text
            
            and r1, r2, r3
            and r3, r0, 0xffff
            and r1, r1, 0xa5a5

            or r1, r2, r3
            or r3, r0, 0xffff
            or r1, r1, 0xa5a5

            add r1, r1, 32767
            add r0, r3, -32768
            add r3, r0, -1
            add r2, r1, 1

            sub r1, r1, 32767
            sub r0, r3, -32768
            sub r3, r0, -1
            sub r2, r1, 1


