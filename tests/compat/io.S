#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

            .text

            reg_rd 0x3ff48000, 7, 0
            reg_wr 0x3ff48000, 7, 0, 42

            i2c_rd 0x10, 7, 0, 0
            i2c_wr 0x23, 0x42, 7, 0, 1

            adc r0, 1, 2

            tsens r0, 42

