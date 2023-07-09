"""
Simple example showing how to control a GPIO pin from the ULP coprocessor.

The GPIO port is configured to be attached to the RTC module, and then set
to OUTPUT mode. To avoid re-initializing the GPIO on every wakeup, a magic
token gets set in memory.

After every change of state, the ULP is put back to sleep again until the
next wakeup. The ULP wakes up every 500ms to change the state of the GPIO
pin. An LED attached to the GPIO pin would toggle on and off every 500ms.

The end of the python script has a loop to show the value of the magic token
and the current state, so you can confirm the magic token gets set and watch
the state value changing. If the loop is stopped (Ctrl-C), the LED attached
to the GPIO pin continues to blink, because the ULP runs independently from
the main processor.
"""

from esp32 import ULP
from machine import mem32
from esp32_ulp import src_to_binary

source = """\
# constants from:
# https://github.com/espressif/esp-idf/blob/1cb31e5/components/soc/esp32/include/soc/soc.h 
#define DR_REG_RTCIO_BASE            0x3ff48400

# constants from:
# https://github.com/espressif/esp-idf/blob/1cb31e5/components/soc/esp32/include/soc/rtc_io_reg.h 
#define RTC_IO_TOUCH_PAD2_REG        (DR_REG_RTCIO_BASE + 0x9c)
#define RTC_IO_TOUCH_PAD2_MUX_SEL_M  (BIT(19))
#define RTC_GPIO_OUT_REG             (DR_REG_RTCIO_BASE + 0x0)
#define RTC_GPIO_ENABLE_REG          (DR_REG_RTCIO_BASE + 0xc)
#define RTC_GPIO_ENABLE_S            14
#define RTC_GPIO_OUT_DATA_S          14

# constants from:
# https://github.com/espressif/esp-idf/blob/1cb31e5/components/soc/esp32/include/soc/rtc_io_channel.h 
#define RTCIO_GPIO2_CHANNEL          12

# When accessed from the RTC module (ULP) GPIOs need to be addressed by their channel number
.set gpio, RTCIO_GPIO2_CHANNEL
.set token, 0xcafe  # magic token

.text
magic: .long 0
state: .long 0

.global entry
entry:
  # load magic flag
  move r0, magic
  ld r1, r0, 0

  # test if we have initialised already
  sub r1, r1, token
  jump after_init, eq  # jump if magic == token (note: "eq" means the last instruction (sub) resulted in 0)

init:
  # connect GPIO to ULP (0: GPIO connected to digital GPIO module, 1: GPIO connected to analog RTC module)
  WRITE_RTC_REG(RTC_IO_TOUCH_PAD2_REG, RTC_IO_TOUCH_PAD2_MUX_SEL_M, 1, 1);

  # GPIO shall be output, not input (this also enables a pull-down by default)
  WRITE_RTC_REG(RTC_GPIO_ENABLE_REG, RTC_GPIO_ENABLE_S + gpio, 1, 1)

  # store that we're done with initialisation
  move r0, magic
  move r1, token
  st r1, r0, 0

after_init:
  move r1, state
  ld r0, r1, 0

  move r2, 1
  sub r0, r2, r0  # toggle state
  st r0, r1, 0  # store updated state

  jumpr on, 0, gt  # if r0 (state) > 0, jump to 'on'
  jump off  # else jump to 'off'

on:
  # turn on led (set GPIO)
  WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 1)
  jump exit

off:
  # turn off led (clear GPIO)
  WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 0)
  jump exit

exit:
  halt  # go back to sleep until next wakeup period
"""

binary = src_to_binary(source, cpu="esp32")  # cpu is esp32 or esp32s2

load_addr, entry_addr = 0, 8

ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

ulp = ULP()
ulp.set_wakeup_period(0, 500000)  # use timer0, wakeup after 500000usec (0.5s)
ulp.load_binary(load_addr, binary)

ulp.run(entry_addr)

while True:
    print(hex(mem32[ULP_MEM_BASE + load_addr] & ULP_DATA_MASK),  # magic token
          hex(mem32[ULP_MEM_BASE + load_addr + 4] & ULP_DATA_MASK)  # current state
          )
