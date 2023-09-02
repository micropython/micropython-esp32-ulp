.set  offs, 0x20
.set  lab1, 0x01

.text
LDL   R1, R2, 0x20
LDL   R1, R2, offs
LDH   R1, R2, 0x20
LDH   R1, R2, offs

STL   R1, R2, 0x20
STL   R1, R2, offs
STL   R1, R2, offs, 1
STL   R1, R2, offs, lab1

STH   R1, R2, 0x20
STH   R1, R2, offs
STH   R1, R2, offs, 1
STH   R1, R2, offs, lab1

ST32  R1, R2, 0x10, 1
ST32  R1, R2, offs, lab1

STI32 R1, R2, 1
STI32 R1, R2, lab1

STI   R1, R2
STI   R1, R2, 1
STI   R1, R2, lab1

STO   0x20
STO   offs
