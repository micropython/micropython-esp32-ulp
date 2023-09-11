#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

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
