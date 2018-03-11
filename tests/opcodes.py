from uctypes import UINT32, BFUINT32, BF_POS, BF_LEN
from esp32_ulp.opcodes import make_ins, make_ins_struct_def, delay

OPCODE_DELAY = 4
LAYOUT_DELAY = """
        cycles : 16     # Number of cycles to sleep
        unused : 12     # Unused
        opcode : 4      # Opcode (OPCODE_DELAY)
"""


def test_make_ins_struct_def():
    sd = make_ins_struct_def(LAYOUT_DELAY)
    assert set(sd) == {'cycles', 'unused', 'opcode', 'all'}
    # TODO check if the expected values are correct (bitfield order)
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
    # TODO: check if the expected value is correct (byte order, bitfield order)
    expected = 0x40000023
    assert _delay.all == expected, '%x != %x' % (_delay.all, expected)


test_make_ins_struct_def()
test_make_ins()

