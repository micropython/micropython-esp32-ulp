#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

#include "soc/rtc_cntl_reg.h"
#include "soc/soc_ulp.h"

  reg_rd 0x012, 1, 2
  reg_rd 0x234, 3, 4
  reg_rd 0x345, 5, 6

  reg_wr 0x012, 1, 2, 1
  reg_wr 0x234, 3, 4, 1
  reg_wr 0x345, 5, 6, 1

  WRITE_RTC_REG(0x3ff484a8, 1, 2, 3)
  READ_RTC_REG(0x3ff484a8, 1, 2)
  WRITE_RTC_REG(0x3ff48904, 1, 2, 3)
  READ_RTC_REG(0x3ff48904, 1, 2)
