from tools.disassemble import decode_instruction
import esp32_ulp.opcodes as opcodes
import ubinascii

tests = []


def test(param):
    tests.append(param)


def hex_to_int(sequence):
    byte_sequence = ubinascii.unhexlify(sequence)
    return int.from_bytes(byte_sequence, 'little')


def assert_decode(sequence, expected_struct, expected_name):
    i = hex_to_int(sequence)

    ins, name = decode_instruction(i)

    assert ins is expected_struct, 'incorrect instruction struct'
    assert name == expected_name, '%s != %s' % (name, expected_name)


def assert_decode_exception(sequence, expected_message):
    i = hex_to_int(sequence)

    try:
        decode_instruction(i)
    except Exception as e:
        assert str(e) == expected_message, str(e)
        raised = True
    else:
        raised = False

    assert raised, 'Exception not raised'


@test
def test_unknown_instruction():
    assert_decode_exception("10000001", 'Unknown instruction')


# All hex sequences were generated using our assembler.
# Note: disassembled instructions always show field values according
# to what is actually encoded into the binary instruction, not as per
# original assembly code.
# For example in JUMP instructions in the source code one would
# specify jump offsets in bytes (e.g. 4 bytes) but in the actual
# instruction offset encoded in the binary instruction will be in
# words (1 word = 4 bytes).
# The disassembled instructions would therefore show as "JUMP 1"
# for what was originally "JUMP 4" in the source code.@test
@test
def test_all_instructions():
    # OPCODE_WR_REG = 1
    assert_decode("00000010", opcodes._wr_reg, 'REG_WR 0x0, 0, 0, 0')

    # OPCODE_RD_REG = 2
    assert_decode("00000020", opcodes._rd_reg, 'REG_RD 0x0, 0, 0')

    # OPCODE_I2C = 3
    assert_decode("00000030", opcodes._i2c, 'I2C_RD 0, 0, 0, 0')
    assert_decode("00000038", opcodes._i2c, 'I2C_WR 0, 0, 0, 0')

    # OPCODE_DELAY = 4
    assert_decode("00000040", opcodes._delay, 'NOP')
    assert_decode("01000040", opcodes._delay, 'WAIT 1')

    # OPCODE_ADC = 5
    assert_decode("00000050", opcodes._adc, 'ADC r0, 0, 0')

    # OPCODE_ST = 6
    assert_decode("00000068", opcodes._st, 'ST r0, r0, 0')

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_REG
    assert_decode("00000070", opcodes._alu_reg, 'ADD r0, r0, r0')
    assert_decode("00002070", opcodes._alu_reg, 'SUB r0, r0, r0')
    assert_decode("00004070", opcodes._alu_reg, 'AND r0, r0, r0')
    assert_decode("00006070", opcodes._alu_reg, 'OR r0, r0, r0')
    assert_decode("00008070", opcodes._alu_reg, "MOVE r0, r0")
    assert_decode("0000a070", opcodes._alu_reg, 'LSH r0, r0, r0')
    assert_decode("0000c070", opcodes._alu_reg, 'RSH r0, r0, r0')

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_IMM
    assert_decode("00000072", opcodes._alu_imm, 'ADD r0, r0, 0')
    assert_decode("00002072", opcodes._alu_imm, 'SUB r0, r0, 0')
    assert_decode("00004072", opcodes._alu_imm, 'AND r0, r0, 0')
    assert_decode("00006072", opcodes._alu_imm, 'OR r0, r0, 0')
    assert_decode("00008072", opcodes._alu_imm, "MOVE r0, 0")
    assert_decode("0000a072", opcodes._alu_imm, 'LSH r0, r0, 0')
    assert_decode("0000c072", opcodes._alu_imm, 'RSH r0, r0, 0')

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_CNT
    assert_decode("00004074", opcodes._alu_cnt, 'STAGE_RST')
    assert_decode("00000074", opcodes._alu_cnt, 'STAGE_INC 0')
    assert_decode("00002074", opcodes._alu_cnt, 'STAGE_DEC 0')

    # OPCODE_BRANCH = 8, SUB_OPCODE_BX (IMM)
    assert_decode("00000080", opcodes._bx, 'JUMP 0')
    assert_decode("00004080", opcodes._bx, 'JUMP 0, EQ')
    assert_decode("00008080", opcodes._bx, 'JUMP 0, OV')

    # OPCODE_BRANCH = 8, SUB_OPCODE_BX (REG)
    assert_decode("00002080", opcodes._bx, 'JUMP r0')
    assert_decode("00006080", opcodes._bx, 'JUMP r0, EQ')
    assert_decode("0000a080", opcodes._bx, 'JUMP r0, OV')

    # OPCODE_BRANCH = 8, SUB_OPCODE_BR
    assert_decode("00000082", opcodes._br, 'JUMPR 0, 0, LT')
    assert_decode("00000182", opcodes._br, 'JUMPR 0, 0, GE')

    # OPCODE_BRANCH = 8, SUB_OPCODE_BX
    assert_decode("00000084", opcodes._bs, 'JUMPS 0, 0, LT')
    assert_decode("00800084", opcodes._bs, 'JUMPS 0, 0, GE')
    assert_decode("00000184", opcodes._bs, 'JUMPS 0, 0, LE')

    # OPCODE_END = 9, SUB_OPCODE_END
    assert_decode("01000090", opcodes._end, 'WAKE')

    # OPCODE_END = 9, SUB_OPCODE_SLEEP
    assert_decode("00000092", opcodes._sleep, 'SLEEP 0')

    # OPCODE_TSENS = 10
    assert_decode("000000a0", opcodes._tsens, 'TSENS r0, 0')

    # OPCODE_HALT = 11
    assert_decode("000000b0", opcodes._halt, 'HALT')

    # OPCODE_LD = 13
    assert_decode("000000d0", opcodes._ld, 'LD r0, r0, 0')


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
