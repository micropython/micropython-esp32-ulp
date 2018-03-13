            .text

            reg_rd 0x3ff48000, 7, 0
            reg_wr 0x3ff48000, 7, 0, 42

            i2c_rd 0x10, 7, 0, 0
            i2c_wr 0x23, 0x42, 7, 0, 1

            adc r0, 1, 2
