#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

from uctypes import UINT32, BFUINT32, BF_POS, BF_LEN
from esp32_ulp.opcodes_s2 import make_ins, make_ins_struct_def
from esp32_ulp.opcodes_s2 import get_reg, get_imm, get_cond, arg_qualify, parse_int, eval_arg, ARG, REG, IMM, SYM, COND
from esp32_ulp.assemble import SymbolTable, ABS, REL, TEXT
import esp32_ulp.opcodes_s2 as opcodes

OPCODE_DELAY = 4
LAYOUT_DELAY = """
    cycles : 16     # Number of cycles to sleep
    unused : 12     # Unused
    opcode : 4      # Opcode (OPCODE_DELAY)
"""


def test_make_ins_struct_def():
    sd = make_ins_struct_def(LAYOUT_DELAY)
    assert set(sd) == {'cycles', 'unused', 'opcode', 'all'}
    assert sd['cycles'] == BFUINT32 | 0 << BF_POS | 16 << BF_LEN
    assert sd['unused'] == BFUINT32 | 16 << BF_POS | 12 << BF_LEN
    assert sd['opcode'] == BFUINT32 | 28 << BF_POS | 4 << BF_LEN
    assert sd['all'] == UINT32


def test_make_ins():
    _delay = make_ins(LAYOUT_DELAY)
    _delay.cycles = 0x23
    _delay.unused = 0
    _delay.opcode = OPCODE_DELAY
    assert _delay.cycles == 0x23
    assert _delay.unused == 0
    assert _delay.opcode == OPCODE_DELAY
    assert _delay.all == 0x40000023


def test_arg_qualify():
    assert arg_qualify('r0') == ARG(REG, 0, 'r0')
    assert arg_qualify('R3') == ARG(REG, 3, 'R3')
    assert arg_qualify('0') == ARG(IMM, 0, '0')
    assert arg_qualify('-1') == ARG(IMM, -1, '-1')
    assert arg_qualify('1') == ARG(IMM, 1, '1')
    assert arg_qualify('0x20') == ARG(IMM, 32, '0x20')
    assert arg_qualify('0100') == ARG(IMM, 64, '0100')
    assert arg_qualify('0o100') == ARG(IMM, 64, '0o100')
    assert arg_qualify('0b1000') == ARG(IMM, 8, '0b1000')
    assert arg_qualify('eq') == ARG(COND, 'eq', 'eq')
    assert arg_qualify('Eq') == ARG(COND, 'eq', 'Eq')
    assert arg_qualify('EQ') == ARG(COND, 'eq', 'EQ')

    # for the next tests, ensure the opcodes module has a SymbolTable
    opcodes.symbols = SymbolTable({}, {}, {})
    opcodes.symbols.set_sym('const', ABS, None, 42)  # constant as defined by .set
    opcodes.symbols.set_sym('entry', REL, TEXT, 4)  # label pointing to code

    assert arg_qualify('1+1') == ARG(IMM, 2, '1+1')
    assert arg_qualify('const >> 1') == ARG(IMM, 21, 'const >> 1')
    assert arg_qualify('entry') == ARG(SYM, (REL, TEXT, 4), 'entry')  # symbols should not (yet) be evaluated
    assert arg_qualify('entry + const') == ARG(IMM, 46, 'entry + const')

    # clean up
    opcodes.symbols = None


def test_get_reg():
    assert get_reg('r0') == 0
    assert get_reg('R3') == 3


def test_get_imm():
    assert get_imm('42') == 42


def test_get_cond():
    assert get_cond('Eq') == 'eq'


def test_eval_arg():
    opcodes.symbols = SymbolTable({}, {}, {})
    opcodes.symbols.set_sym('const', ABS, None, 42)  # constant
    opcodes.symbols.set_sym('raise', ABS, None, 99)  # constant using a Python keyword as a name (allowed)

    assert eval_arg('1+1') == 2
    assert eval_arg('1+const') == 43
    assert eval_arg('raise*2/3') == 66
    assert eval_arg('raise-const') == 57
    assert eval_arg('(raise-const)*2') == 114
    assert eval_arg('const    % 5') == 2
    assert eval_arg('const + 0x19af') == 0x19af + 42
    assert eval_arg('const & ~2') == 40
    assert eval_arg('const << 3') == 336
    assert eval_arg('const >> 1') == 21
    assert eval_arg('(const|4)&0xf') == 0xe

    assert eval_arg('0x7') == 7
    assert eval_arg('010') == 8
    assert eval_arg('-0x7') == -7  # negative
    assert eval_arg('~0x7') == -8  # complement

    assert_raises(ValueError, eval_arg, 'evil()')
    assert_raises(ValueError, eval_arg, 'def cafe()')
    assert_raises(ValueError, eval_arg, '1 ^ 2')
    assert_raises(ValueError, eval_arg, '!100')

    # clean up
    opcodes.symbols = None


def assert_raises(exception, func, *args, message=None):
    try:
        func(*args)
    except exception as e:
        raised = True
        actual_message = e.args[0]
    else:
        raised = False
    assert raised
    if message:
        assert actual_message == message, '%s == %s' % (actual_message, message)


def test_reg_direct_ulp_addressing():
    """
    Test direct ULP addressing of peripheral registers
    input must be <= 0x3ff (10 bits)
    periph_sel == high 2 bits from input
    addr == low 8 bits from input
    """

    ins = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_RD_REG)
    """)

    ins.all = opcodes.i_reg_rd("0x0", "0", "0")
    assert ins.periph_sel == 0
    assert ins.addr == 0x0

    ins.all = opcodes.i_reg_rd("0x012", "0", "0")
    assert ins.periph_sel == 0
    assert ins.addr == 0x12

    ins.all = opcodes.i_reg_rd("0x123", "0", "0")
    assert ins.periph_sel == 1
    assert ins.addr == 0x23

    ins.all = opcodes.i_reg_rd("0x2ee", "0", "0")
    assert ins.periph_sel == 2
    assert ins.addr == 0xee

    ins.all = opcodes.i_reg_rd("0x3ff", "0", "0")
    assert ins.periph_sel == 3
    assert ins.addr == 0xff

    # anything bigger than 0x3ff must be a valid full address
    assert_raises(ValueError, opcodes.i_reg_rd, "0x400", "0", "0")


def test_reg_address_translations_s2():
    """
    Test addressing of ESP32-S2 peripheral registers using full DPORT bus addresses
    """

    ins = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_RD_REG)
    """)

    # direct ULP address is derived from full address as follows:
    # full:0x3f4084a8 == ulp:(0x3f4084a8-DR_REG_RTCCNTL_BASE) / 4
    # full:0x3f4084a8 == ulp:(0x3f4084a8-0x3f408000) / 4
    # full:0x3f4084a8 == ulp:0x4a8 / 4
    # full:0x3f4084a8 == ulp:0x12a
    # see: https://github.com/espressif/binutils-esp32ulp/blob/249ec34/gas/config/tc-esp32ulp_esp32s2.c#L78
    ins.all = opcodes.i_reg_rd("0x3f4084a8", "0", "0")
    assert ins.periph_sel == 1  # high 2 bits of 0x12a
    assert ins.addr == 0x2a  # low 8 bits of 0x12a


def test_reg_address_translations_s2_sens():
    """
    Test addressing of ESP32-S2 peripheral registers using full DPORT bus addresses
    """

    ins = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_RD_REG)
    """)

    # direct ULP address is derived from full address as follows:
    # full:0x3f408904 == ulp:(0x3f408904-DR_REG_RTCCNTL_BASE) / 4
    # full:0x3f408904 == ulp:(0x3f408904-0x3f408000) / 4
    # full:0x3f408904 == ulp:0x904 / 4
    # full:0x3f408904 == ulp:0x241
    # see: https://github.com/espressif/binutils-esp32ulp/blob/249ec34/gas/config/tc-esp32ulp_esp32s2.c#L78
    ins.all = opcodes.i_reg_rd("0x3f408904", "0", "0")
    assert ins.periph_sel == 2  # high 2 bits of 0x241
    assert ins.addr == 0x41  # low 8 bits of 0x241


def test_reg_address_translations_s3():
    """
    Test addressing of ESP32-S3 peripheral registers using full DPORT bus addresses
    """

    ins = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_RD_REG)
    """)

    # direct ULP address is derived from full address as follows:
    # full:0x600084a8 == ulp:(0x600084a8-DR_REG_RTCCNTL_BASE) / 4
    # full:0x600084a8 == ulp:(0x600084a8-0x60008000) / 4
    # full:0x600084a8 == ulp:0x4a8 / 4
    # full:0x600084a8 == ulp:0x12a
    # see: https://github.com/espressif/binutils-esp32ulp/blob/249ec34/gas/config/tc-esp32ulp_esp32s2.c#L78
    ins.all = opcodes.i_reg_rd("0x600084a8", "0", "0")
    assert ins.periph_sel == 1  # high 2 bits of 0x12a
    assert ins.addr == 0x2a  # low 8 bits of 0x12a


def test_reg_address_translations_s3_sens():
    """
    Test addressing of ESP32-S3 peripheral registers using full DPORT bus addresses
    """

    ins = make_ins("""
    addr : 8        # Address within either RTC_CNTL, RTC_IO, or SARADC
    periph_sel : 2  # Select peripheral: RTC_CNTL (0), RTC_IO(1), SARADC(2)
    unused : 8      # Unused
    low : 5         # Low bit
    high : 5        # High bit
    opcode : 4      # Opcode (OPCODE_RD_REG)
    """)

    # direct ULP address is derived from full address as follows:
    # full:0x60008904 == ulp:(0x60008904-DR_REG_RTCCNTL_BASE) / 4
    # full:0x60008904 == ulp:(0x60008904-0x60008000) / 4
    # full:0x60008904 == ulp:0x904 / 4
    # full:0x60008904 == ulp:0x241
    # see: https://github.com/espressif/binutils-esp32ulp/blob/249ec34/gas/config/tc-esp32ulp_esp32s2.c#L78
    ins.all = opcodes.i_reg_rd("0x60008904", "0", "0")
    assert ins.periph_sel == 2  # high 2 bits of 0x241
    assert ins.addr == 0x41  # low 8 bits of 0x241


test_make_ins_struct_def()
test_make_ins()
test_arg_qualify()
test_get_reg()
test_get_imm()
test_get_cond()
test_eval_arg()
test_reg_direct_ulp_addressing()
test_reg_address_translations_s2()
test_reg_address_translations_s3()
test_reg_address_translations_s2_sens()
test_reg_address_translations_s3_sens()
