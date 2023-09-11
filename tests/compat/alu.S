#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

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

            lsh r0, r1, r2
            lsh r2, r3, 1

            rsh r3, r2, r1
            rsh r3, r2, 31

            move r0, r1
            move r0, 42

            stage_rst
            stage_inc 42
            stage_dec 23

