"""
Example for: ESP32-S3

Very basic example showing how to read a GPIO pin from the ULP and access
that data from the main CPU.

In this case GPIO4 is being read. Note that the ULP needs to refer to GPIOs
via their RTC channel number. You can see the mapping in this file:
https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s3/include/soc/rtc_io_channel.h#L33

If you change to a different GPIO number, make sure to modify both the channel
number and also the RTC_IO_TOUCH_PAD2_* references appropriately. The best place
to see the mappings might be this table here (notice the "real GPIO numbers" as
comments to each line):
https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s3/rtc_io_periph.c#L60

The timer is set to a rather long period, so you can watch the data value
change as you change the GPIO input (see loop at the end).
"""

from esp32 import ULP
from machine import mem32

from esp32_ulp import src_to_binary

source = """\
#define DR_REG_RTCIO_BASE            0x60008400
#define RTC_IO_TOUCH_PAD2_REG        (DR_REG_RTCIO_BASE + 0x8c)
#define RTC_IO_TOUCH_PAD2_MUX_SEL_M  (BIT(19))
#define RTC_IO_TOUCH_PAD2_FUN_IE_M   (BIT(13))
#define RTC_GPIO_IN_REG              (DR_REG_RTCIO_BASE + 0x24)
#define RTC_GPIO_IN_NEXT_S           10
#define DR_REG_SENS_BASE             0x60008800
#define SENS_SAR_PERI_CLK_GATE_CONF_REG  (DR_REG_SENS_BASE + 0x104)
#define SENS_IOMUX_CLK_EN            (BIT(31))
.set channel, 2

state:      .long 0

entry:
            # enable IOMUX clock
            WRITE_RTC_FIELD(SENS_SAR_PERI_CLK_GATE_CONF_REG, SENS_IOMUX_CLK_EN, 1)

            # connect GPIO to the RTC subsystem so the ULP can read it
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD2_REG, RTC_IO_TOUCH_PAD2_MUX_SEL_M, 1, 1)

            # switch the GPIO into input mode
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD2_REG, RTC_IO_TOUCH_PAD2_FUN_IE_M, 1, 1)

            # read the GPIO's current state into r0
            READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + channel, 1)

            # set r3 to the memory address of "state"
            move r3, state

            # store what was read into r0 into the "state" variable
            st r0, r3, 0

            # halt ULP co-processor (until it gets woken up again)
            halt
"""

binary = src_to_binary(source, cpu="esp32s2")  # cpu is esp32 or esp32s2

load_addr, entry_addr = 0, 4

ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

ulp = ULP()
ulp.set_wakeup_period(0, 50000)  # use timer0, wakeup after 50.000 cycles
ulp.load_binary(load_addr, binary)

mem32[ULP_MEM_BASE + load_addr] = 0x0  # initialise state to 0
ulp.run(entry_addr)

while True:
    print(hex(mem32[ULP_MEM_BASE + load_addr] & ULP_DATA_MASK))

