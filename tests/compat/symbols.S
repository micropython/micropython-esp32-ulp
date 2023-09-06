#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

            .text

            .set constant42, 42
.set notindented, 1

start:      move r0, data0
            move r1, data1
            move r2, constant42
            move r3, notindented

            # count from 0 .. 42 in stage register
            stage_rst
loop1:      stage_inc 1
            jumps loop1, 42, lt

            # count from 0 .. 42 in r0
            move r0, 0
loop2:      add r0, r0, 1
            jumpr loop2, 42, lt

end:        jump start

            .data

data0:      .long 1000
data1:      .long 1001

