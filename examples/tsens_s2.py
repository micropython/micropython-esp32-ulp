#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT


"""
Example for: ESP32-S2

Example showing how to use the TSENS instruction from the ULP
and access temperature data from the main CPU.

Note that the temperature sensor clock needs to be enabled for the TSENS instruction to complete.

"""

from esp32 import ULP
from machine import mem32
from esp32_ulp import src_to_binary
from time import sleep

source = """\
# constants from:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s2/include/soc/reg_base.h
#define DR_REG_SENS_BASE            0x3f408800

# constants from:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s2/include/soc/sens_reg.h
#define SENS_SAR_TSENS_CTRL2_REG          (DR_REG_SENS_BASE + 0x0054)
#define SENS_TSENS_CLKGATE_EN_M  (BIT(15))

.set token, 0xACED

.text
magic: .long 0
temperature_data:  .long 0

.global entry
entry:
    move r3, magic
    ld r0, r3, 0
    jumpr start, token, eq #check if we have already initialized
    
init:
    # Set SENS_TSENS_CLKGATE_EN to enable temperature sensor clock.
    WRITE_RTC_REG(SENS_SAR_TSENS_CTRL2_REG, SENS_TSENS_CLKGATE_EN_M, 1, 1)
    
    # Store temperature_data memory location in r2
    move r2, temperature_data
    
    # store that we're done with initialisation
    move r0, token
    st r0, r3, 0
    
start:
    tsens r0, 1000 # make measurement for 1000 clock cycles
    st r0, r2, 0 # store the temperature in memory to be read by main CPU
    halt # go back to sleep until next wakeup period
"""

binary = src_to_binary(source, cpu="esp32s2")  # cpu is esp32 or esp32s2

load_addr, entry_addr = 0, 8

ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

ulp = ULP()
ulp.set_wakeup_period(0, 500000)  # use timer0, wakeup after 500000usec (0.5s)
ulp.load_binary(load_addr, binary)

ulp.run(entry_addr)

while True:
    magic_token = hex(mem32[ULP_MEM_BASE + load_addr] & ULP_DATA_MASK)
    current_temperature = 0.4386*(mem32[ULP_MEM_BASE + load_addr + 4] & ULP_DATA_MASK)-20.52
    print(magic_token, current_temperature)
    sleep(0.5)