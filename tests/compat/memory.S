#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

            .text

            ld r0, r1, 0
            ld r2, r3, 4

            st r0, r1, 0
            st r3, r2, 8

