#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

"""
Example for: ESP32-S2

This example creates a PWM-like dimming effect using self-modifying ULP code.
The ULP program rewrites the `WAIT` instructions to control on/off LED durations,
simulating a variable duty cycle.

Note:
The `WAIT` instruction uses an immediate operand (fixed value) for delay cycles. However, we can change the lower half of memory
to modify these values at runtime, simulating variable wait times via registers.
"""

from esp32 import ULP
from machine import mem32
from esp32_ulp import src_to_binary
from time import sleep

source = """\
# Pin with LED: (0 to 21)
.set led_pin,                        4

# constants from:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s2/include/soc/reg_base.h
#define DR_REG_RTCIO_BASE            0x3f408400

# constants from:
# Espressif Technical Reference Manual (TRM) Chapter 5.15 Register 5.63:
#define RTCIO_TOUCH_PADn_REG               (DR_REG_RTCIO_BASE + 0x84 + 4 * led_pin)
#define RTCIO_TOUCH_PADn_MUX_SEL_M         (BIT(19))

# constants from:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s2/include/soc/rtc_io_reg.h
#define RTC_GPIO_OUT_REG             (DR_REG_RTCIO_BASE + 0x0)
#define RTC_GPIO_ENABLE_REG          (DR_REG_RTCIO_BASE + 0xc)
#define RTC_GPIO_ENABLE_S            10
#define RTC_GPIO_OUT_DATA_S          10

.global entry
program_init:
  # connect GPIO to ULP (0: GPIO connected to digital GPIO module, 1: GPIO connected to analog RTC module)
  WRITE_RTC_REG(RTCIO_TOUCH_PADn_REG, RTCIO_TOUCH_PADn_MUX_SEL_M, 1, 1);

  # enable GPIO as output, not input (this also enables a pull-down by default)
  WRITE_RTC_REG(RTC_GPIO_ENABLE_REG, RTC_GPIO_ENABLE_S + led_pin, 1, 1)

set_waits:  add r0, r0, 200 # Increase r0 (delay time)
            move r3, wait_off
            st r0, r3, 0 # Overwrite wait_off with new delay value
            
            move r2, 0xFFFF
            sub r1, r2, r0 # Calculate complementary delay time     
            move r3, wait_on
            st r1, r3, 0 # Overwrite wait_on with new value

            WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + led_pin, 1, 0) # turn off LED (clear GPIO)
wait_off:   wait 0 # Placeholder; value overwritten dynamically
            WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + led_pin, 1, 1) # turn on LED (set GPIO)
wait_on:    wait 0 # Placeholder; value overwritten dynamically
  
jump set_waits # Loop program

"""

binary = src_to_binary(source, cpu="esp32s2")  # cpu is esp32 or esp32s2

load_addr, entry_addr = 0, 0

ULP_MEM_BASE = 0x50000000

ulp = ULP()
ulp.load_binary(load_addr, binary)

ulp.run(entry_addr)

while True:
    print(hex(mem32[ULP_MEM_BASE + 40])) # show that the WAIT cycles are changing
    sleep(0.5)
