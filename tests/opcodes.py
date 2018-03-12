from uctypes import UINT32, BFUINT32, BF_POS, BF_LEN
from esp32_ulp.opcodes import make_ins, make_ins_struct_def

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


test_make_ins_struct_def()
test_make_ins()

