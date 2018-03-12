"""
ESP32 ULP Co-Processor Instructions
"""

from uctypes import struct, addressof, LITTLE_ENDIAN, UINT32, BFUINT32, BF_POS, BF_LEN

from .soc import *

# Opcodes, Sub-Opcodes, Modes, ...

OPCODE_WR_REG = 1
OPCODE_RD_REG = 2

RD_REG_PERIPH_RTC_CNTL = 0
RD_REG_PERIPH_RTC_IO = 1
RD_REG_PERIPH_SENS = 2
RD_REG_PERIPH_RTC_I2C = 3

OPCODE_DELAY = 4

OPCODE_ST = 6
SUB_OPCODE_ST = 4

OPCODE_ALU = 7
SUB_OPCODE_ALU_REG = 0
SUB_OPCODE_ALU_IMM = 1
ALU_SEL_ADD = 0
ALU_SEL_MOV = 4

OPCODE_BRANCH = 8
SUB_OPCODE_BX = 0
BX_JUMP_TYPE_DIRECT = 0
BX_JUMP_TYPE_ZERO = 1
BX_JUMP_TYPE_OVF = 2
SUB_OPCODE_B = 1
B_CMP_L = 0
B_CMP_GE = 1

OPCODE_END = 9
SUB_OPCODE_END = 0
SUB_OPCODE_SLEEP = 1

OPCODE_HALT = 11

OPCODE_LD = 13


def make_ins_struct_def(layout):
    lines = layout.strip().splitlines()
    pos = 0  # bitfield definitions start from lsb
    struct_def = {}
    for line in lines:
        bitfield = line.split('#', 1)[0]  # get rid of comment
        name, width = bitfield.split(':', 1)
        name = name.strip()
        width = int(width.strip())
        struct_def[name] = BFUINT32 | pos << BF_POS | width << BF_LEN
        pos += width
    if pos != 32:
        raise ValueError('make_ins: bit field widths must sum up to 32. [%s]' % layout)
    struct_def['all'] = UINT32
    return struct_def


def make_ins(layout):
    """
    transform textual instruction layout description into a ready-to-use uctypes struct
    """
    struct_def = make_ins_struct_def(layout)
    instruction = bytearray(4)
    return struct(addressof(instruction), struct_def, LITTLE_ENDIAN)


# instruction structure definitions

_wr_reg = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    data : 8        # 8 bits of data to write
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_WR_REG)
""")


_rd_reg = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_WR_REG)
""")


_delay = make_ins("""
    cycles : 16     # Number of cycles to sleep
    unused : 12     # Unused
    opcode : 4      # Opcode (OPCODE_DELAY)
""")


_st = make_ins("""
    dreg : 2        # Register which contains data to store
    sreg : 2        # Register which contains address in RTC memory (expressed in words)
    unused1 : 6     # Unused
    offset : 11     # Offset to add to sreg
    unused2 : 4     # Unused
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_ST)
    opcode : 4      # Opcode (OPCODE_ST)
""")


_alu_reg = make_ins("""
    dreg : 2        # Destination register
    sreg : 2        # Register with operand A
    treg : 2        # Register with operand B
    unused : 15     # Unused
    sel : 4         # Operation to perform, one of ALU_SEL_xxx
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_ALU_REG)
    opcode : 4      # Opcode (OPCODE_ALU)
""")


_alu_imm = make_ins("""
    dreg : 2        # Destination register
    sreg : 2        # Register with operand A
    imm : 16        # Immediate value of operand B
    unused : 1      # Unused
    sel : 4         # Operation to perform, one of ALU_SEL_xxx
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_ALU_IMM)
    opcode : 4      # Opcode (OPCODE_ALU)
""")


_bx = make_ins("""
    dreg : 2        # Register which contains target PC, expressed in words (used if .reg == 1)
    addr : 11       # Target PC, expressed in words (used if .reg == 0)
    unused : 8      # Unused
    reg : 1         # Target PC in register (1) or immediate (0)
    type : 3        # Jump condition (BX_JUMP_TYPE_xxx)
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_BX)
    opcode : 4      # Opcode (OPCODE_BRANCH)
""")


_b = make_ins("""
    imm : 16        # Immediate value to compare against
    cmp : 1         # Comparison to perform: B_CMP_L or B_CMP_GE
    offset : 7      # Absolute value of target PC offset w.r.t. current PC, expressed in words
    sign : 1        # Sign of target PC offset: 0: positive, 1: negative
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_B)
    opcode : 4      # Opcode (OPCODE_BRANCH)
""")


_end = make_ins("""
    wakeup : 1      # Set to 1 to wake up chip
    unused : 24     # Unused
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_END)
    opcode : 4      # Opcode (OPCODE_END)
""")


_sleep = make_ins("""
    cycle_sel : 4   # Select which one of SARADC_ULP_CP_SLEEP_CYCx_REG to get the sleep duration from
    unused : 21     # Unused
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_SLEEP)
    opcode : 4      # Opcode (OPCODE_END)
""")


_halt = make_ins("""
    unused : 28     # Unused
    opcode : 4      # Opcode (OPCODE_HALT)
""")


_ld = make_ins("""
    dreg : 2        # Register where the data should be loaded to
    sreg : 2        # Register which contains address in RTC memory (expressed in words)
    unused1 : 6     # Unused
    offset : 11     # Offset to add to sreg
    unused2 : 7     # Unused
    opcode : 4      # Opcode (OPCODE_LD)
""")


# assembler opcode definitions


def _soc_reg_to_ulp_periph_sel(reg):
    # Map SoC peripheral register to periph_sel field of RD_REG and WR_REG instructions.
    ret = 3
    if reg < DR_REG_RTCCNTL_BASE:
        raise ValueError("invalid register base")
    elif reg < DR_REG_RTCIO_BASE:
        ret = RD_REG_PERIPH_RTC_CNTL
    elif reg < DR_REG_SENS_BASE:
        ret = RD_REG_PERIPH_RTC_IO
    elif reg < DR_REG_RTC_I2C_BASE:
        ret = RD_REG_PERIPH_SENS
    elif reg < DR_REG_IO_MUX_BASE:
        ret = RD_REG_PERIPH_RTC_I2C
    else:
        raise ValueError("invalid register base")
    return ret


def wr_reg(reg, low_bit, high_bit, val):
    _wr_reg.addr = (reg & 0xff) >> 2
    _wr_reg.periph_sel = _soc_reg_to_ulp_periph_sel(reg)
    _wr_reg.data = val
    _wr_reg.low = low_bit
    _wr_reg.high = high_bit
    _wr_reg.opcode = OPCODE_WR_REG
    return _wr_reg.all


def rd_reg(reg, low_bit, high_bit):
    _rd_reg.addr = (reg & 0xff) >> 2
    _rd_reg.periph_sel = _soc_reg_to_ulp_periph_sel(reg)
    _rd_reg.unused = 0
    _rd_reg.low = low_bit
    _rd_reg.high = high_bit
    _rd_reg.opcode = OPCODE_RD_REG
    return _rd_reg.all


def delay(cycles):
    _delay.cycles = cycles
    _delay.unused = 0
    _delay.opcode = OPCODE_DELAY
    return _delay.all


def st(reg_val, reg_addr, offset):
    _st.dreg = reg_val
    _st.sreg = reg_addr
    _st.unused1 = 0
    _st.offset = offset
    _st.unused2 = 0
    _st.sub_opcode = SUB_OPCODE_ST
    _st.opcode = OPCODE_ST
    return _st.all


def halt():
    _halt.unused = 0
    _halt.opcode = OPCODE_HALT
    return _halt.all


def ld(reg_dest, reg_addr, offset):
    _ld.dreg = reg_dest
    _ld.sreg = reg_addr
    _ld.unused1 = 0
    _ld.offset = offset
    _ld.unused2 = 0
    _ld.opcode = OPCODE_LD
    return _ld.all


def addr(reg_dest, reg_src1, reg_src2):
    _alu_reg.dreg = reg_dest
    _alu_reg.sreg = reg_src1
    _alu_reg.treg = reg_src2
    _alu_reg.unused = 0
    _alu_reg.sel = ALU_SEL_ADD
    _alu_reg.sub_opcode = SUB_OPCODE_ALU_REG
    _alu_reg.opcode = OPCODE_ALU
    return _alu_reg.all


def movr(reg_dest, reg_src):
    _alu_reg.dreg = reg_dest
    _alu_reg.sreg = reg_src
    _alu_reg.treg = 0
    _alu_reg.unused = 0
    _alu_reg.sel = ALU_SEL_MOV
    _alu_reg.sub_opcode = SUB_OPCODE_ALU_REG
    _alu_reg.opcode = OPCODE_ALU
    return _alu_reg.all


def addi(reg_dest, reg_src, imm):
    _alu_imm.dreg = reg_dest
    _alu_imm.sreg = reg_src
    _alu_imm.imm = imm
    _alu_imm.unused = 0
    _alu_imm.sel = ALU_SEL_ADD
    _alu_imm.sub_opcode = SUB_OPCODE_ALU_IMM
    _alu_imm.opcode = OPCODE_ALU
    return _alu_imm.all


def movi(reg_dest, imm):
    _alu_imm.dreg = reg_dest
    _alu_imm.sreg = 0
    _alu_imm.imm = imm
    _alu_imm.unused = 0
    _alu_imm.sel = ALU_SEL_MOV
    _alu_imm.sub_opcode = SUB_OPCODE_ALU_IMM
    _alu_imm.opcode = OPCODE_ALU
    return _alu_imm.all


def wake():
    _end.wakeup = 1
    _end.unused = 0
    _end.sub_opcode = SUB_OPCODE_END
    _end.opcode = OPCODE_END
    return _end.all


def sleep_cycle_sel(timer_idx):
    _sleep.cycle_sel = timer_idx
    _sleep.unused = 0
    _sleep.sub_opcode = SUB_OPCODE_SLEEP
    _sleep.opcode = OPCODE_END
    return _sleep.all


def bge(pc_offset, imm_value):
    _b.imm = imm_value
    _b.cmp = B_CMP_GE
    _b.offset = abs(pc_offset)
    _b.sign = 0 if pc_offset >= 0 else 1
    _b.sub_opcode = SUB_OPCODE_B
    _b.opcode = OPCODE_BRANCH
    return _b.all


def bl(pc_offset, imm_value):
    _b.imm = imm_value
    _b.cmp = B_CMP_L
    _b.offset = abs(pc_offset)
    _b.sign = 0 if pc_offset >= 0 else 1
    _b.sub_opcode = SUB_OPCODE_B
    _b.opcode = OPCODE_BRANCH
    return _b.all


def bxr(reg_pc):
    _bx.dreg = reg_pc
    _bx.addr = 0
    _bx.unused = 0
    _bx.reg = 1
    _bx.type = BX_JUMP_TYPE_DIRECT
    _bx.sub_opcode = SUB_OPCODE_BX
    _bx.opcode = OPCODE_BRANCH
    return _bx.all


def bxi(imm_pc):
    _bx.dreg = 0
    _bx.addr = imm_pc
    _bx.unused = 0
    _bx.reg = 0
    _bx.type = BX_JUMP_TYPE_DIRECT
    _bx.sub_opcode = SUB_OPCODE_BX
    _bx.opcode = OPCODE_BRANCH
    return _bx.all
