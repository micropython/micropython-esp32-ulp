            .text

            nop
            nop
            nop

            .data

            .space 4
            .space 8, 0xFF
            .space 1
            .align 4
            .space 3

            # a section start will be automatically 32bit-aligned:
            .bss

            .space 10
            # a section end will be automatically 32bit-aligned
