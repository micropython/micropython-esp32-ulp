from uctypes import UINT32, BFUINT32, BF_POS, BF_LEN
from esp32_ulp.opcodes import make_ins, make_ins_struct_def
from esp32_ulp.opcodes import get_reg, get_imm, get_cond, arg_qualify, eval_arg, ARG, REG, IMM, SYM, COND
from esp32_ulp.assemble import SymbolTable, ABS, REL, TEXT
import esp32_ulp.opcodes as opcodes

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
    opcodes.symbols.set_sym('raise', ABS, None, 99)  # constant using a python keyword as name (is allowed)

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

    assert_raises(ValueError, eval_arg, 'evil()')
    assert_raises(ValueError, eval_arg, 'def cafe()')
    assert_raises(ValueError, eval_arg, '1 ^ 2')
    assert_raises(ValueError, eval_arg, '!100')

    # clean up
    opcodes.symbols = None


def assert_raises(exception, func, *args):
    try:
        func(*args)
    except exception:
        raised = True
    else:
        raised = False
    assert raised


test_make_ins_struct_def()
test_make_ins()
test_arg_qualify()
test_get_reg()
test_get_imm()
test_get_cond()
test_eval_arg()