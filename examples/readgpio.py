#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

"""
Example for: ESP32

Very basic example showing how to read a GPIO pin from the ULP and access
that data from the main CPU.

In this case GPIO4 is being read. Note that the ULP needs to refer to GPIOs
via their RTC channel number. You can see the mapping in this file:
https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/rtc_io_channel.h#L51

If you change to a different GPIO number, make sure to modify both the channel
number and also the RTC_IO_TOUCH_PAD0_* references appropriately. The best place
to see the mappings might be this table here (notice the "real GPIO numbers" as
comments to each line):
https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/rtc_io_periph.c#L53

The timer is set to a rather long period, so you can watch the data value
change as you change the GPIO input (see loop at the end).
"""

from esp32 import ULP
from machine import mem32

from esp32_ulp import src_to_binary

source = """\
#define DR_REG_RTCIO_BASE            0x3ff48400
#define RTC_IO_TOUCH_PAD0_REG        (DR_REG_RTCIO_BASE + 0x94)
#define RTC_IO_TOUCH_PAD0_MUX_SEL_M  (BIT(19))
#define RTC_IO_TOUCH_PAD0_FUN_IE_M   (BIT(13))
#define RTC_GPIO_IN_REG              (DR_REG_RTCIO_BASE + 0x24)
#define RTC_GPIO_IN_NEXT_S           14
.set channel, 10  # 10 is the channel no. of gpio4

state:      .long 0

entry:
            # connect GPIO to the RTC subsystem so the ULP can read it
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)

            # switch the GPIO into input mode
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_FUN_IE_M, 1, 1)

            # read the GPIO's current state into r0
            READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + channel, 1)

            # set r3 to the memory address of "state"
            move r3, state

            # store what was read into r0 into the "state" variable
            st r0, r3, 0

            # halt ULP co-processor (until it gets woken up again)
            halt
"""

binary = src_to_binary(source, cpu="esp32")  # cpu is esp32 or esp32s2

load_addr, entry_addr = 0, 4

ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

ulp = ULP()
ulp.set_wakeup_period(0, 50000)  # use timer0; wake up after 50,000 cycles
ulp.load_binary(load_addr, binary)

mem32[ULP_MEM_BASE + load_addr] = 0x0  # initialize state to 0
ulp.run(entry_addr)

while True:
    print(hex(mem32[ULP_MEM_BASE + load_addr] & ULP_DATA_MASK))

