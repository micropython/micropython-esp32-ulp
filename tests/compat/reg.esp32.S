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
