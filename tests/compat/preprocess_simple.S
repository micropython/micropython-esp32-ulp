#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

#define GPIO 2
#define BASE 0x100
#define ADDR (BASE + GPIO)

entry:
  move r0, GPIO
  move r1, ADDR
