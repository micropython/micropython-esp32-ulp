"""
ESP32 ULP Co-Processor Instructions
"""

from ucollections import namedtuple
from uctypes import struct, addressof, LITTLE_ENDIAN, UINT32, BFUINT32, BF_POS, BF_LEN

from .util import split_tokens, validate_expression

# XXX dirty hack: use a global for the symbol table
symbols = None

# Opcodes, Sub-Opcodes, Modes, ...

OPCODE_WR_REG = 1
OPCODE_RD_REG = 2

DR_REG_MAX_DIRECT = 0x3ff
RD_REG_PERIPH_RTC_CNTL = 0
RD_REG_PERIPH_RTC_IO = 1
RD_REG_PERIPH_SENS = 2
RD_REG_PERIPH_RTC_I2C = 3

OPCODE_I2C = 3
SUB_OPCODE_I2C_RD = 0
SUB_OPCODE_I2C_WR = 1

OPCODE_DELAY = 4

OPCODE_ADC = 5

OPCODE_ST = 6
SUB_OPCODE_ST_AUTO = 1
# Note: SUB_OPCODE_ST_OFFSET should be 3
# But in binutils-gdb they hardcoded the value to 2
# This appears to be a bug, if one looks at the Technical
# Reference Manual of the ESP32-S2.
#
# This issue is reported as a pull-request with fix:
# https://github.com/espressif/binutils-gdb/pull/2
#
# We'll hard code this to 2 for now, until this is resolved in
# binutils-gdb or the Technical Reference Manual is updated.
SUB_OPCODE_ST_OFFSET = 2  # should be 3
SUB_OPCODE_ST = 4

OPCODE_ALU = 7
SUB_OPCODE_ALU_REG = 0
SUB_OPCODE_ALU_IMM = 1
ALU_SEL_ADD = 0
ALU_SEL_SUB = 1
ALU_SEL_AND = 2
ALU_SEL_OR = 3
ALU_SEL_MOV = 4
ALU_SEL_LSH = 5
ALU_SEL_RSH = 6
SUB_OPCODE_ALU_CNT = 2
ALU_SEL_STAGE_INC = 0
ALU_SEL_STAGE_DEC = 1
ALU_SEL_STAGE_RST = 2

OPCODE_BRANCH = 8
# https://github.com/espressif/binutils-esp32ulp/blob/d61f86f97eda43fc118df30d019fc062aaa6bc8d/include/opcode/esp32ulp_esp32.h#L85
SUB_OPCODE_B = 0
SUB_OPCODE_BX = 1
SUB_OPCODE_BS = 2
BX_JUMP_TYPE_DIRECT = 0
BX_JUMP_TYPE_ZERO = 1
BX_JUMP_TYPE_OVF = 2
# https://github.com/espressif/binutils-esp32ulp/blob/d61f86f97eda43fc118df30d019fc062aaa6bc8d/gas/config/tc-esp32ulp.h#L91
B_CMP_L = 0
B_CMP_G = 1
B_CMP_E = 2
JUMPS_EQ = 4
JUMPS_GT = 3
JUMPS_LT = 1
JUMPS_LE = 5
JUMPS_GE = 7

OPCODE_END = 9
SUB_OPCODE_END = 0
SUB_OPCODE_SLEEP = 1

OPCODE_TSENS = 10

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
    opcode : 4      # Opcode (OPCODE_RD_REG)
""")


_i2c = make_ins("""
    sub_addr : 8    # address within I2C slave
    data : 8        # Data to write (not used for read)
    low : 3         # low bit
    high : 3        # high bit
    i2c_sel : 4     # select i2c slave via SENS_I2C_SLAVE_ADDRx
    unused : 1      # Unused
    rw : 1          # Write (1) or read (0)
    opcode : 4      # Opcode (OPCODE_I2C)
""")


_delay = make_ins("""
    cycles : 16     # Number of cycles to sleep
    unused : 12     # Unused
    opcode : 4      # Opcode (OPCODE_DELAY)
""")


_tsens = make_ins("""
    dreg : 2        # Register where to store TSENS result
    delay : 14      # Number of cycles needed to obtain a measurement
    unused : 12     # Unused
    opcode : 4      # Opcode (OPCODE_TSENS)
""")


_adc = make_ins("""
    dreg : 2        # Register where to store ADC result
    mux : 4         # Select SARADC pad (mux + 1)
    sar_sel : 1     # Select SARADC0 (0) or SARADC1 (1)
    unused1 : 1     # Unused
    cycles : 16     # TBD, cycles used for measurement
    unused2 : 4     # Unused
    opcode: 4       # Opcode (OPCODE_ADC)
""")


_st = make_ins("""
    sreg : 2        # Register which contains data to store
    dreg : 2        # Register which contains address in RTC memory (expressed in words)
    label : 2       # Data label
    upper : 1       # Write low (0) or high (1) half-word
    wr_way : 2      # Write the (0) full-word or with label (1) or without label (3)
    unused1 : 1     # Unused
    offset : 11     # Offset to add to dreg
    unused2 : 4     # Unused
    sub_opcode : 3  # Sub opcode (SUB_OPCODE_ST)
    opcode : 4      # Opcode (OPCODE_ST)
""")


_alu_reg = make_ins("""
    dreg : 2        # Destination register
    sreg : 2        # Register with operand A
    treg : 2        # Register with operand B
    unused1 : 15    # Unused
    sel : 4         # Operation to perform, one of ALU_SEL_xxx
    unused2 : 1     # Unused
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_ALU_REG)
    opcode : 4      # Opcode (OPCODE_ALU)
""")


_alu_imm = make_ins("""
    dreg : 2        # Destination register
    sreg : 2        # Register with operand A
    imm : 16        # Immediate value of operand B
    unused1 : 1     # Unused
    sel : 4         # Operation to perform, one of ALU_SEL_xxx
    unused2 : 1     # Unused
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_ALU_IMM)
    opcode : 4      # Opcode (OPCODE_ALU)
""")


_alu_cnt = make_ins("""
    unused1 : 4     # Unused
    imm : 8         # Immediate value (to inc / dec stage counter)
    unused2 : 9     # Unused
    sel : 4         # Operation to perform, one of ALU_SEL_xxx
    unused3 : 1     # Unused
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_ALU_CNT)
    opcode : 4      # Opcode (OPCODE_ALU)
""")


_bx = make_ins("""
    dreg : 2        # Register which contains target PC, expressed in words (used if .reg == 1)
    addr : 11       # Target PC, expressed in words (used if .reg == 0)
    unused1 : 8     # Unused
    reg : 1         # Target PC in register (1) or immediate (0)
    type : 3        # Jump condition (BX_JUMP_TYPE_xxx)
    unused2 : 1     # Unused
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_BX)
    opcode : 4      # Opcode (OPCODE_BRANCH)
""")


_b = make_ins("""
    imm : 16        # Immediate value to compare against
    cmp : 2         # Comparison to perform: BRCOND_LT or BRCOND_GE
    offset : 7      # Absolute value of target PC offset w.r.t. current PC, expressed in words
    sign : 1        # Sign of target PC offset: 0: positive, 1: negative
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_B)
    opcode : 4      # Opcode (OPCODE_BRANCH)
""")


_bs = make_ins("""
    imm : 8         # Immediate value to compare against
    unused : 7      # Unused
    cmp : 3         # Comparison to perform: BRCOND_LT, GT or EQ
    offset : 7      # Absolute value of target PC offset w.r.t. current PC, expressed in words
    sign : 1        # Sign of target PC offset: 0: positive, 1: negative
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_BS)
    opcode : 4      # Opcode (OPCODE_BRANCH)
""")


_end = make_ins("""
    wakeup : 1      # Set to 1 to wake up chip
    unused : 25     # Unused
    sub_opcode : 2  # Sub opcode (SUB_OPCODE_END)
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
    unused2 : 6     # Unused
    rd_upper : 1    # Read low (0) or high (1) half-word
    opcode : 4      # Opcode (OPCODE_LD)
""")


# assembler opcode definitions

REG, IMM, COND, SYM = 0, 1, 2, 3
ARG = namedtuple('ARG', ('type', 'value', 'raw'))


def eval_arg(arg):
    parts = []
    for token in split_tokens(arg):
        if symbols.has_sym(token):
            _, _, sym_value = symbols.get_sym(token)
            parts.append(str(sym_value))
        else:
            parts.append(token)
    parts = "".join(parts)
    if not validate_expression(parts):
        raise ValueError('Unsupported expression: %s' % parts)
    return eval(parts)


def arg_qualify(arg):
    """
    look at arg and qualify its type:
    REG(ister), IMM(ediate) value

    then convert arg into a int value, e.g. 'R1' -> 1 or '0x20' -> 32.

    return result as ARG namedtuple
    """
    arg_lower = arg.lower()
    if len(arg) == 2:
        if arg_lower[0] == 'r' and arg[1] in '0123456789':
            reg = int(arg[1])
            if 0 <= reg <= 3:
                return ARG(REG, reg, arg)
            raise ValueError('arg_qualify: valid registers are r0, r1, r2, r3. Given: %s' % arg)
        if arg_lower in ['--', 'eq', 'ov', 'lt', 'gt', 'ge', 'le']:
            return ARG(COND, arg_lower, arg)
    try:
        return ARG(IMM, int(arg), arg)
    except ValueError:
        pass
    try:
        entry = symbols.get_sym(arg)
    except KeyError:
        return ARG(IMM, int(eval_arg(arg)), arg)
    else:
        return ARG(SYM, entry, arg)


def get_reg(arg):
    if isinstance(arg, str):
        arg = arg_qualify(arg)
    if arg.type == REG:
        return arg.value
    raise TypeError('wanted: register, got: %s' % arg.raw)


def get_imm(arg):
    if isinstance(arg, str):
        arg = arg_qualify(arg)
    if arg.type == IMM:
        return arg.value
    if arg.type == SYM:
        return symbols.resolve_absolute(arg.value)
    raise TypeError('wanted: immediate, got: %s' % arg.raw)


get_abs = get_imm


def get_rel(arg):
    if isinstance(arg, str):
        arg = arg_qualify(arg)
    if arg.type == IMM:
        if arg.value & 3 != 0:  # bitwise version of: arg.value % 4 != 0
            raise ValueError('Relative offset must be a multiple of 4')
        return IMM, arg.value >> 2  # bitwise version of: arg.value // 4
    if arg.type == SYM:
        return SYM, symbols.resolve_relative(arg.value)
    raise TypeError('wanted: immediate, got: %s' % arg.raw)


def get_cond(arg):
    if isinstance(arg, str):
        arg = arg_qualify(arg)
    if arg.type == COND:
        return arg.value
    raise TypeError('wanted: condition, got: %s' % arg.raw)


def _soc_reg_to_ulp_periph_sel(reg):
    # Accept peripheral register addresses of either the S2 or S3
    # Since the address in the reg_rd or reg_wr instruction is an
    # offset and not the actual address, and since the range of
    # peripheral register addresses is the same for both the S2
    # and S3, we will accept addresses in either address range.
    # This allows us to avoid intruducing an additional cpu type
    # for the S3, which is otherwise identical (binary format) to
    # the S2.
    if 0x3f408000 <= reg <= 0x3f40afff:  # ESP32-S2 address range
        socmod = 'soc_s2'
    elif 0x60008000 <= reg <= 0x6000afff:  # ESP32-S3 address range
        socmod = 'soc_s3'
    # Accept original ESP32 range too
    # because binutils-gdb, when using cpu esp32s2 is broken
    # and does not accept the address ranges of the esp32s2.
    # As a nice side-effect some assembly written for an ESP32
    # would work as-is when re-assembled for an ESP32-S2,
    # because many (not all!) peripheral registers live at the
    # same offset on all 3 ESP32s.
    elif 0x3ff48000 <= reg <= 0x3ff4afff:  # original ESP32 address range
        socmod = 'soc'
    else:
        raise ValueError("invalid register base")

    relative_import = 1 if '/' in __file__ else 0
    soc = __import__(socmod, None, None, [], relative_import)

    # Map SoC peripheral register to periph_sel field of RD_REG and WR_REG instructions.
    if reg < soc.DR_REG_RTCCNTL_BASE:
        raise ValueError("invalid register base")
    elif reg < soc.DR_REG_RTCIO_BASE:
        ret = RD_REG_PERIPH_RTC_CNTL
    elif reg < soc.DR_REG_SENS_BASE:
        ret = RD_REG_PERIPH_RTC_IO
    elif reg < soc.DR_REG_RTC_I2C_BASE:
        ret = RD_REG_PERIPH_SENS
    elif reg < soc.DR_REG_IO_MUX_BASE:
        ret = RD_REG_PERIPH_RTC_I2C
    else:
        raise ValueError("invalid register base")
    return ret


def i_reg_wr(reg, high_bit, low_bit, val):
    reg = get_imm(reg)
    if reg <= DR_REG_MAX_DIRECT:  # see https://github.com/espressif/binutils-esp32ulp/blob/master/gas/config/tc-esp32ulp_esp32.c
        _wr_reg.addr = reg & 0xff
        _wr_reg.periph_sel = (reg & 0x300) >> 8
    else:
        _wr_reg.addr = (reg & 0xff) >> 2
        _wr_reg.periph_sel = _soc_reg_to_ulp_periph_sel(reg)
    _wr_reg.data = get_imm(val)
    _wr_reg.low = get_imm(low_bit)
    _wr_reg.high = get_imm(high_bit)
    _wr_reg.opcode = OPCODE_WR_REG
    return _wr_reg.all


def i_reg_rd(reg, high_bit, low_bit):
    reg = get_imm(reg)
    if reg <= DR_REG_MAX_DIRECT:  # see https://github.com/espressif/binutils-esp32ulp/blob/master/gas/config/tc-esp32ulp_esp32.c
        _rd_reg.addr = reg & 0xff
        _rd_reg.periph_sel = (reg & 0x300) >> 8
    else:
        _rd_reg.addr = (reg & 0xff) >> 2
        _rd_reg.periph_sel = _soc_reg_to_ulp_periph_sel(reg)
    _rd_reg.unused = 0
    _rd_reg.low = get_imm(low_bit)
    _rd_reg.high = get_imm(high_bit)
    _rd_reg.opcode = OPCODE_RD_REG
    return _rd_reg.all


def i_i2c_rd(sub_addr, high_bit, low_bit, slave_sel):
    _i2c.sub_addr = get_imm(sub_addr)
    _i2c.data = 0
    _i2c.low = get_imm(low_bit)
    _i2c.high = get_imm(high_bit)
    _i2c.i2c_sel = get_imm(slave_sel)
    _i2c.unused = 0
    _i2c.rw = 0
    _i2c.opcode = OPCODE_I2C
    return _i2c.all


def i_i2c_wr(sub_addr, value, high_bit, low_bit, slave_sel):
    _i2c.sub_addr = get_imm(sub_addr)
    _i2c.data = get_imm(value)
    _i2c.low = get_imm(low_bit)
    _i2c.high = get_imm(high_bit)
    _i2c.i2c_sel = get_imm(slave_sel)
    _i2c.unused = 0
    _i2c.rw = 1
    _i2c.opcode = OPCODE_I2C
    return _i2c.all


def i_nop():
    _delay.cycles = 0
    _delay.unused = 0
    _delay.opcode = OPCODE_DELAY
    return _delay.all


def i_wait(cycles):
    _delay.cycles = get_imm(cycles)
    _delay.unused = 0
    _delay.opcode = OPCODE_DELAY
    return _delay.all


def i_tsens(reg_dest, delay):
    _tsens.dreg = get_reg(reg_dest)
    _tsens.delay = get_imm(delay)
    _tsens.unused = 0
    _tsens.opcode = OPCODE_TSENS
    return _tsens.all


def i_adc(reg_dest, adc_idx, mux, _not_used=None):
    _adc.dreg = get_reg(reg_dest)
    _adc.mux = get_imm(mux)
    _adc.sar_sel = get_imm(adc_idx)
    _adc.unused1 = 0
    _adc.cycles = 0
    _adc.unused2 = 0
    _adc.opcode = OPCODE_ADC
    return _adc.all


def i_st_manual(reg_val, reg_addr, offset, label, upper, wr_way):
    _st.dreg = get_reg(reg_addr)
    _st.sreg = get_reg(reg_val)
    _st.label = get_imm(label)
    _st.upper = upper
    _st.wr_way = wr_way
    _st.unused1 = 0
    _st.offset = get_imm(offset) // 4
    _st.unused2 = 0
    _st.sub_opcode = SUB_OPCODE_ST
    _st.opcode = OPCODE_ST
    return _st.all


def i_stl(reg_val, reg_addr, offset, label=None):
    return i_st_manual(reg_val, reg_addr, offset, label if label else "0", 0, 1 if label else 3)


def i_sth(reg_val, reg_addr, offset, label=None):
    return i_st_manual(reg_val, reg_addr, offset, label if label else "0", 1, 1 if label else 3)


def i_st(reg_val, reg_addr, offset):
    return i_stl(reg_val, reg_addr, offset)


def i_st32(reg_val, reg_addr, offset, label):
    return i_st_manual(reg_val, reg_addr, offset, label, 0, 0)


def i_st_auto(reg_val, reg_addr, label, wr_way):
    _st.dreg = get_reg(reg_addr)
    _st.sreg = get_reg(reg_val)
    _st.label = get_imm(label)
    _st.upper = 0
    _st.wr_way = wr_way
    _st.unused1 = 0
    _st.offset = 0
    _st.unused2 = 0
    _st.sub_opcode = SUB_OPCODE_ST_AUTO
    _st.opcode = OPCODE_ST
    return _st.all


def i_sto(offset):
    _st.dreg = 0
    _st.sreg = 0
    _st.label = 0
    _st.upper = 0
    _st.wr_way = 0
    _st.unused1 = 0
    _st.offset = get_imm(offset) // 4
    _st.unused2 = 0
    _st.sub_opcode = SUB_OPCODE_ST_OFFSET
    _st.opcode = OPCODE_ST
    return _st.all


def i_sti(reg_val, reg_addr, label=None):
    return i_st_auto(reg_val, reg_addr, label if label else "0", 1 if label else 3)


def i_sti32(reg_val, reg_addr, label):
    return i_st_auto(reg_val, reg_addr, label, 0)


def i_halt():
    _halt.unused = 0
    _halt.opcode = OPCODE_HALT
    return _halt.all


def i_ld_manual(reg_dest, reg_addr, offset, rd_upper):
    _ld.dreg = get_reg(reg_dest)
    _ld.sreg = get_reg(reg_addr)
    _ld.unused1 = 0
    _ld.offset = get_imm(offset) // 4
    _ld.unused2 = 0
    _ld.rd_upper = rd_upper
    _ld.opcode = OPCODE_LD
    return _ld.all


def i_ldl(reg_dest, reg_addr, offset):
    return i_ld_manual(reg_dest, reg_addr, offset, 0)


def i_ldh(reg_dest, reg_addr, offset):
    return i_ld_manual(reg_dest, reg_addr, offset, 1)


def i_ld(reg_dest, reg_addr, offset):
    return i_ldl(reg_dest, reg_addr, offset)


def i_move(reg_dest, reg_imm_src):
    # this is the only ALU instruction with 2 args: move r0, r1
    dest = get_reg(reg_dest)
    src = arg_qualify(reg_imm_src)
    if src.type == REG:
        _alu_reg.dreg = dest
        _alu_reg.sreg = src.value
        _alu_reg.treg = src.value  # XXX undocumented, this is the value binutils-esp32 uses
        _alu_reg.unused1 = 0
        _alu_reg.sel = ALU_SEL_MOV
        _alu_reg.unused2 = 0
        _alu_reg.sub_opcode = SUB_OPCODE_ALU_REG
        _alu_reg.opcode = OPCODE_ALU
        return _alu_reg.all
    if src.type == IMM or src.type == SYM:
        _alu_imm.dreg = dest
        _alu_imm.sreg = 0
        _alu_imm.imm = get_abs(src)
        _alu_imm.unused1 = 0
        _alu_imm.sel = ALU_SEL_MOV
        _alu_imm.unused2 = 0
        _alu_imm.sub_opcode = SUB_OPCODE_ALU_IMM
        _alu_imm.opcode = OPCODE_ALU
        return _alu_imm.all
    raise TypeError('unsupported operand: %s' % src.raw)


def _alu3(reg_dest, reg_src1, reg_imm_src2, alu_sel):
    """
    ALU instructions with 3 args, like e.g. add r1, r2, r3
    """
    dest = get_reg(reg_dest)
    src1 = get_reg(reg_src1)
    src2 = arg_qualify(reg_imm_src2)
    if src2.type == REG:
        _alu_reg.dreg = dest
        _alu_reg.sreg = src1
        _alu_reg.treg = src2.value
        _alu_reg.unused1 = 0
        _alu_reg.sel = alu_sel
        _alu_reg.unused2 = 0
        _alu_reg.sub_opcode = SUB_OPCODE_ALU_REG
        _alu_reg.opcode = OPCODE_ALU
        return _alu_reg.all
    if src2.type == IMM or src2.type == SYM:
        _alu_imm.dreg = dest
        _alu_imm.sreg = src1
        _alu_imm.imm = get_abs(src2)
        _alu_imm.unused1 = 0
        _alu_imm.sel = alu_sel
        _alu_imm.unused2 = 0
        _alu_imm.sub_opcode = SUB_OPCODE_ALU_IMM
        _alu_imm.opcode = OPCODE_ALU
        return _alu_imm.all
    raise TypeError('unsupported operand: %s' % src2.raw)


def i_add(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_ADD)


def i_sub(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_SUB)


def i_and(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_AND)


def i_or(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_OR)


def i_lsh(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_LSH)


def i_rsh(reg_dest, reg_src1, reg_imm_src2):
    return _alu3(reg_dest, reg_src1, reg_imm_src2, ALU_SEL_RSH)


def _alu_stage(imm, alu_sel):
    """
    Stage counter instructions with 1 arg: stage_inc / stage_dec
    """
    imm = get_imm(imm)
    _alu_cnt.unused1 = 0
    _alu_cnt.imm = imm
    _alu_cnt.unused2 = 0
    _alu_cnt.sel = alu_sel
    _alu_cnt.sub_opcode = SUB_OPCODE_ALU_CNT
    _alu_cnt.opcode = OPCODE_ALU
    return _alu_cnt.all


def i_stage_inc(imm):
    return _alu_stage(imm, ALU_SEL_STAGE_INC)


def i_stage_dec(imm):
    return _alu_stage(imm, ALU_SEL_STAGE_DEC)


def i_stage_rst():
    return _alu_stage('0', ALU_SEL_STAGE_RST)


def i_wake():
    _end.wakeup = 1
    _end.unused = 0
    _end.sub_opcode = SUB_OPCODE_END
    _end.opcode = OPCODE_END
    return _end.all


# NOTE: Technically the S2 no longer has the SLEEP instruction, but
# we're keeping it, since esp32ulp-elf-as happily assembles it.
# It's now emitted as a WAIT so we'll do the same.
def i_sleep(cycles):
    return i_wait(cycles)


def i_jump(target, condition='--'):
    target = arg_qualify(target)
    condition = get_cond(condition)
    if condition == 'eq':
        jump_type = BX_JUMP_TYPE_ZERO
    elif condition == 'ov':
        jump_type = BX_JUMP_TYPE_OVF
    elif condition == '--':  # means unconditional
        jump_type = BX_JUMP_TYPE_DIRECT
    else:
        raise ValueError("invalid flags condition")
    if target.type == IMM or target.type == SYM:
        _bx.dreg = 0
        # we track label addresses in 32bit words, but immediate values are in bytes and need to get divided by 4.
        _bx.addr = get_abs(target) if target.type == SYM else get_abs(target) >> 2  # bitwise version of "// 4"
        _bx.unused1 = 0
        _bx.reg = 0
        _bx.type = jump_type
        _bx.sub_opcode = SUB_OPCODE_BX
        _bx.unused2 = 0
        _bx.opcode = OPCODE_BRANCH
        return _bx.all
    if target.type == REG:
        _bx.dreg = target.value
        _bx.addr = 0
        _bx.unused1 = 0
        _bx.reg = 1
        _bx.type = jump_type
        _bx.unused2 = 0
        _bx.sub_opcode = SUB_OPCODE_BX
        _bx.opcode = OPCODE_BRANCH
        return _bx.all
    raise TypeError('unsupported operand: %s' % target.raw)


def _jump_relr(threshold, cond, offset):
    """
    Equivalent of I_JUMP_RELR macro in binutils-gdb esp32ulp
    """
    _b.imm = threshold
    _b.cmp = cond
    _b.offset = abs(offset)
    _b.sign = 0 if offset >= 0 else 1
    _b.sub_opcode = SUB_OPCODE_B
    _b.opcode = OPCODE_BRANCH
    return _b.all


def i_jumpr(offset, threshold, condition):
    offset_type, offset = get_rel(offset)
    threshold = get_imm(threshold)
    condition = get_cond(condition)
    if condition in ('le', 'ge'):
        if condition == 'le':
            cmp_op = B_CMP_L
        elif condition == 'ge':
            cmp_op = B_CMP_G

        # jump to target
        first_ins = _jump_relr(threshold, cmp_op, offset)

        # jump over prev JUMPR
        if (offset_type == IMM and offset < 0) or offset_type == SYM:
            # adjust for the additional JUMPR instruction
            # for IMM offsets, the offset is relative to the 2nd instruction, so only backwards jumps need adjusting
            # for SYM offsets, label offsets already include the extra instruction, so both directions need adjusting
            offset -= 1
        second_ins = _jump_relr(threshold, B_CMP_E, offset)
        return (first_ins, second_ins)

    elif condition == 'lt':
        cmp_op = B_CMP_L
    elif condition == 'gt':
        cmp_op = B_CMP_G
    elif condition == 'eq':
        cmp_op = B_CMP_E
    else:
        raise ValueError("invalid comparison condition")
    return _jump_relr(threshold, cmp_op, offset)


def _jump_rels(threshold, cond, offset):
    """
    Equivalent of I_JUMP_RELS macro in binutils-gdb esp32ulp
    """
    _bs.imm = threshold
    _bs.cmp = cond
    _bs.offset = abs(offset)
    _bs.sign = 0 if offset >= 0 else 1
    _bs.sub_opcode = SUB_OPCODE_BS
    _bs.opcode = OPCODE_BRANCH
    return _bs.all


def i_jumps(offset, threshold, condition):
    offset_type, offset = get_rel(offset)
    if (offset_type == IMM):
        # This makes our assembler behave exactly like binutils-gdb, even
        # though its behaviour is incorrect. binutils-gdb does not divide
        # immediate offsets by 4 (i.e. it does not convert bytes to words)
        # for JUMPS instructions, even though it does so for all other JUMP
        # instructions, and even though the assembler for the original
        # ESP32 divides immediate offsets by 4 for JUMPS instructions.
        #
        # The issue is reported as a pull-request with a fix here:
        # https://github.com/espressif/binutils-gdb/pull/1
        #
        # Once the issue is fixed in binutils-gdb, this code here should be
        # removed.
        offset = offset << 2  # bug in binutils-gdb

    threshold = get_imm(threshold)
    condition = get_cond(condition)
    if condition == 'lt':
        cmp_op = JUMPS_LT
    elif condition == 'le':
        cmp_op = JUMPS_LE
    elif condition == 'ge':
        cmp_op = JUMPS_GE
    elif condition == 'eq':
        cmp_op = JUMPS_EQ
    elif condition == 'gt':
        cmp_op = JUMPS_GT
    else:
        raise ValueError("invalid comparison condition")

    return _jump_rels(threshold, cmp_op, offset)


def no_of_instr(opcode, args):
    if opcode == 'jumpr' and get_cond(args[2]) in ('le', 'ge'):
        return 2

    return 1
