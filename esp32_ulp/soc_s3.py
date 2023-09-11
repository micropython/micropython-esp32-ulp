#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

"""
Address / Register definitions for the ESP32-S3 SoC
"""

# Reference:
# https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32s3/include/soc/reg_base.h

DR_REG_UART_BASE                        = 0x60000000
DR_REG_SPI1_BASE                        = 0x60002000
DR_REG_SPI0_BASE                        = 0x60003000
DR_REG_GPIO_BASE                        = 0x60004000
DR_REG_GPIO_SD_BASE                     = 0x60004f00
DR_REG_FE2_BASE                         = 0x60005000
DR_REG_FE_BASE                          = 0x60006000
DR_REG_EFUSE_BASE                       = 0x60007000
DR_REG_RTCCNTL_BASE                     = 0x60008000
DR_REG_RTCIO_BASE                       = 0x60008400
DR_REG_SENS_BASE                        = 0x60008800
DR_REG_RTC_I2C_BASE                     = 0x60008C00
DR_REG_IO_MUX_BASE                      = 0x60009000
DR_REG_HINF_BASE                        = 0x6000B000
DR_REG_UHCI1_BASE                       = 0x6000C000
DR_REG_I2S_BASE                         = 0x6000F000
DR_REG_UART1_BASE                       = 0x60010000
DR_REG_BT_BASE                          = 0x60011000
DR_REG_I2C_EXT_BASE                     = 0x60013000
DR_REG_UHCI0_BASE                       = 0x60014000
DR_REG_SLCHOST_BASE                     = 0x60015000
DR_REG_RMT_BASE                         = 0x60016000
DR_REG_PCNT_BASE                        = 0x60017000
DR_REG_SLC_BASE                         = 0x60018000
DR_REG_LEDC_BASE                        = 0x60019000
DR_REG_NRX_BASE                         = 0x6001CC00
DR_REG_BB_BASE                          = 0x6001D000
DR_REG_PWM0_BASE                        = 0x6001E000
DR_REG_TIMERGROUP0_BASE                 = 0x6001F000
DR_REG_TIMERGROUP1_BASE                 = 0x60020000
DR_REG_RTC_SLOWMEM_BASE                 = 0x60021000
DR_REG_SYSTIMER_BASE                    = 0x60023000
DR_REG_SPI2_BASE                        = 0x60024000
DR_REG_SPI3_BASE                        = 0x60025000
DR_REG_SYSCON_BASE                      = 0x60026000
DR_REG_APB_CTRL_BASE                    = 0x60026000  # Old name for SYSCON, to be removed
DR_REG_I2C1_EXT_BASE                    = 0x60027000
DR_REG_SDMMC_BASE                       = 0x60028000
DR_REG_PERI_BACKUP_BASE                 = 0x6002A000
DR_REG_TWAI_BASE                        = 0x6002B000
DR_REG_PWM1_BASE                        = 0x6002C000
DR_REG_I2S1_BASE                        = 0x6002D000
DR_REG_UART2_BASE                       = 0x6002E000
DR_REG_USB_SERIAL_JTAG_BASE             = 0x60038000
DR_REG_USB_WRAP_BASE                    = 0x60039000
DR_REG_AES_BASE                         = 0x6003A000
DR_REG_SHA_BASE                         = 0x6003B000
DR_REG_RSA_BASE                         = 0x6003C000
DR_REG_HMAC_BASE                        = 0x6003E000
DR_REG_DIGITAL_SIGNATURE_BASE           = 0x6003D000
DR_REG_GDMA_BASE                        = 0x6003F000
DR_REG_APB_SARADC_BASE                  = 0x60040000
DR_REG_LCD_CAM_BASE                     = 0x60041000
DR_REG_SYSTEM_BASE                      = 0x600C0000
DR_REG_SENSITIVE_BASE                   = 0x600C1000
DR_REG_INTERRUPT_BASE                   = 0x600C2000
DR_REG_EXTMEM_BASE                      = 0x600C4000
DR_REG_ASSIST_DEBUG_BASE                = 0x600CE000
DR_REG_WCL_BASE                         = 0x600D0000
