.data
empty: .long 0
magic: .long 0xc0decafe

.text
REG_WR 0x123, 1, 2, 3

REG_RD 0x321, 2, 1

I2C_RD 3, 2, 1, 0
I2C_WR 0, 1, 2, 3, 4

NOP
WAIT 7

ADC r3, 2, 1

ST r3, r2, 1

ADD r2, r1, r0
SUB r2, r1, r0
AND r2, r1, r0
OR r2, r1, r0
MOVE r2, r1
LSH r2, r1, r0
RSH r2, r1, r0

ADD r2, r1, 0
SUB r2, r1, 0
AND r2, r1, 0
OR r2, r1, 0
MOVE r1, 0
LSH r2, r1, 0
RSH r2, r1, 0

STAGE_RST
STAGE_INC 7
STAGE_DEC 3

JUMP r0
JUMP r1, EQ
JUMP r2, OV

JUMP 0
JUMP 0, EQ
JUMP 0, OV

JUMPR 0, 1, LT
JUMPR 4, 5, GT
JUMPR 8, 7, EQ

JUMPS 0, 1, LT
JUMPS 4, 5, GT
JUMPS 8, 7, EQ
JUMPS 12, 9, LE
JUMPS 16, 11, GE

WAKE
SLEEP 7

TSENS r1, 2

HALT

LD r2, r1, 0

# ESP32-S2 specific instructions
NOP  # marker

LDL R1, R2, 0x20
LDH R1, R2, 0x20

STL R1, R2, 0x20
STL R1, R2, 0x20, 0
STL R1, R2, 0x20, 1

STH R1, R2, 0x20
STH R1, R2, 0x20, 0
STH R1, R2, 0x20, 1

ST32 R1, R2, 0x20, 0
ST32 R1, R2, 0x20, 1

STI R1, R2
STI R1, R2, 0
STI R1, R2, 1

STI32 R1, R2, 0
STI32 R1, R2, 1

STO   0x20

LDL R1, R2, -0x20
LDH R1, R2, -0x20

STL R1, R2, -0x20
STH R1, R2, -0x20
