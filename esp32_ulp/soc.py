#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

"""
Address / Register definitions for the ESP32 SoC
"""

# Reference:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/reg_base.h

DR_REG_DPORT_BASE                       = 0x3ff00000
DR_REG_AES_BASE                         = 0x3ff01000
DR_REG_RSA_BASE                         = 0x3ff02000
DR_REG_SHA_BASE                         = 0x3ff03000
DR_REG_FLASH_MMU_TABLE_PRO              = 0x3ff10000
DR_REG_FLASH_MMU_TABLE_APP              = 0x3ff12000
DR_REG_DPORT_END                        = 0x3ff13FFC
DR_REG_UART_BASE                        = 0x3ff40000
DR_REG_SPI1_BASE                        = 0x3ff42000
DR_REG_SPI0_BASE                        = 0x3ff43000
DR_REG_GPIO_BASE                        = 0x3ff44000
DR_REG_GPIO_SD_BASE                     = 0x3ff44f00
DR_REG_FE2_BASE                         = 0x3ff45000
DR_REG_FE_BASE                          = 0x3ff46000
DR_REG_FRC_TIMER_BASE                   = 0x3ff47000
DR_REG_RTCCNTL_BASE                     = 0x3ff48000
DR_REG_RTCIO_BASE                       = 0x3ff48400
DR_REG_SENS_BASE                        = 0x3ff48800
DR_REG_RTC_I2C_BASE                     = 0x3ff48C00
DR_REG_IO_MUX_BASE                      = 0x3ff49000
DR_REG_HINF_BASE                        = 0x3ff4B000
DR_REG_UHCI1_BASE                       = 0x3ff4C000
DR_REG_I2S_BASE                         = 0x3ff4F000
DR_REG_UART1_BASE                       = 0x3ff50000
DR_REG_BT_BASE                          = 0x3ff51000
DR_REG_I2C_EXT_BASE                     = 0x3ff53000
DR_REG_UHCI0_BASE                       = 0x3ff54000
DR_REG_SLCHOST_BASE                     = 0x3ff55000
DR_REG_RMT_BASE                         = 0x3ff56000
DR_REG_PCNT_BASE                        = 0x3ff57000
DR_REG_SLC_BASE                         = 0x3ff58000
DR_REG_LEDC_BASE                        = 0x3ff59000
DR_REG_EFUSE_BASE                       = 0x3ff5A000
DR_REG_SPI_ENCRYPT_BASE                 = 0x3ff5B000
DR_REG_NRX_BASE                         = 0x3ff5CC00
DR_REG_BB_BASE                          = 0x3ff5D000
DR_REG_PWM0_BASE                        = 0x3ff5E000
DR_REG_TIMERGROUP0_BASE                 = 0x3ff5F000
DR_REG_TIMERGROUP1_BASE                 = 0x3ff60000
DR_REG_RTCMEM0_BASE                     = 0x3ff61000
DR_REG_RTCMEM1_BASE                     = 0x3ff62000
DR_REG_RTCMEM2_BASE                     = 0x3ff63000
DR_REG_SPI2_BASE                        = 0x3ff64000
DR_REG_SPI3_BASE                        = 0x3ff65000
DR_REG_SYSCON_BASE                      = 0x3ff66000
DR_REG_APB_CTRL_BASE                    = 0x3ff66000  # Old name for SYSCON, to be removed
DR_REG_I2C1_EXT_BASE                    = 0x3ff67000
DR_REG_SDMMC_BASE                       = 0x3ff68000
DR_REG_EMAC_BASE                        = 0x3ff69000
DR_REG_CAN_BASE                         = 0x3ff6B000
DR_REG_PWM1_BASE                        = 0x3ff6C000
DR_REG_I2S1_BASE                        = 0x3ff6D000
DR_REG_UART2_BASE                       = 0x3ff6E000
PERIPHS_SPI_ENCRYPT_BASEADDR            = DR_REG_SPI_ENCRYPT_BASE
