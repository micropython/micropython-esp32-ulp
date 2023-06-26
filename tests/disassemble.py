from tools.disassemble import decode_instruction, get_instruction_fields
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


def assert_decode_fields(sequence, expected_field_details):
    i = hex_to_int(sequence)

    ins, _ = decode_instruction(i)

    actual_field_details = get_instruction_fields(ins)

    assert actual_field_details == expected_field_details, '\n- %s \n+ %s' % (actual_field_details, expected_field_details)


@test
def test_unknown_instruction():
    assert_decode_exception("10000001", 'Unknown instruction')


@test
def test_empty_instruction():
    assert_decode_exception("00000000", '<empty>')


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


@test
def test_instruction_field_decoding():
    # OPCODE_WR_REG = 1
    assert_decode_fields("000c8810", [  # REG_WR 0x0, 1, 2, 3
        ('addr'      ,  0, ''),
        ('data'      ,  3, ''),
        ('high'      ,  1, ''),
        ('low'       ,  2, ''),
        ('opcode'    ,  1, ''),
        ('periph_sel',  0, ''),
    ])

    # OPCODE_RD_REG = 2
    assert_decode_fields("03000421", [  # REG_RD 0x3, 2, 1
        ('addr'      ,  3, ''),
        ('high'      ,  2, ''),
        ('low'       ,  1, ''),
        ('opcode'    ,  2, ''),
        ('periph_sel',  0, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_I2C = 3
    assert_decode_fields("03001130", [  # I2C_RD 3, 2, 1, 0
        ('data'      ,  0, ''),
        ('high'      ,  2, ''),
        ('i2c_sel'   ,  0, ''),
        ('low'       ,  1, ''),
        ('opcode'    ,  3, ''),
        ('rw'        ,  0, ''),
        ('sub_addr'  ,  3, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("00011339", [  # I2C_WR 0, 2, 3, 4
        ('data'      ,  1, ''),
        ('high'      ,  2, ''),
        ('i2c_sel'   ,  4, ''),
        ('low'       ,  3, ''),
        ('opcode'    ,  3, ''),
        ('rw'        ,  1, ''),
        ('sub_addr'  ,  0, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_DELAY = 4
    assert_decode_fields("00000040", [  # NOP
        ('cycles'    ,  0, ''),
        ('opcode'    ,  4, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("07000040", [  # WAIT 7
        ('cycles'    ,  7, ''),
        ('opcode'    ,  4, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_ADC = 5
    assert_decode_fields("07000050", [  # ADC r3, 1, 0
        ('cycles'    ,  0, ''),
        ('dreg'      ,  3, ''),
        ('mux'       ,  1, ''),
        ('opcode'    ,  5, ''),
        ('sar_sel'   ,  0, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])

    # OPCODE_ST = 6
    assert_decode_fields("0b000068", [  # ST r3, r2, 0
        ('dreg'      ,  2, ''),
        ('offset'    ,  0, ''),
        ('opcode'    ,  6, ''),
        ('sreg'      ,  3, ''),
        ('sub_opcode',  4, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_REG
    assert_decode_fields("06000070", [  # ADD r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  0, ' (ADD)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06002070", [  # SUB r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  1, ' (SUB)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06004070", [  # AND r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  2, ' (AND)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06006070", [  # OR r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  3, ' (OR)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600a070", [  # LSH r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  5, ' (LSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600c070", [  # RSH r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  6, ' (RSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06000070", [  # ADD r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  0, ' (ADD)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06002070", [  # SUB r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  1, ' (SUB)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06004070", [  # AND r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  2, ' (AND)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06006070", [  # OR r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  3, ' (OR)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("16008070", [  # MOVE r2, r1
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  4, ' (MOVE)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600a070", [  # LSH r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  5, ' (LSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600c070", [  # RSH r2, r1, r0
        ('dreg'      ,  2, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  6, ' (RSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  0, ''),
        ('treg'      ,  0, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_IMM
    assert_decode_fields("06000072", [  # ADD r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  0, ' (ADD)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06002072", [  # SUB r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  1, ' (SUB)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06004072", [  # AND r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  2, ' (AND)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("06006072", [  # OR r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  3, ' (OR)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("01008072", [  # MOVE r1, 0
        ('dreg'      ,  1, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  4, ' (MOVE)'),
        ('sreg'      ,  0, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600a072", [  # LSH r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  5, ' (LSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0600c072", [  # RSH r2, r1, 0
        ('dreg'      ,  2, ''),
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  6, ' (RSH)'),
        ('sreg'      ,  1, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_ALU = 7, SUB_OPCODE_ALU_CNT
    assert_decode_fields("00004074", [  # STAGE_RST
        ('imm'       ,  0, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  2, ' (STAGE_RST)'),
        ('sub_opcode',  2, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])
    assert_decode_fields("70000074", [  # STAGE_INC 7
        ('imm'       ,  7, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  0, ' (STAGE_INC)'),
        ('sub_opcode',  2, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])
    assert_decode_fields("30002074", [  # STAGE_DEC 3
        ('imm'       ,  3, ''),
        ('opcode'    ,  7, ''),
        ('sel'       ,  1, ' (STAGE_DEC)'),
        ('sub_opcode',  2, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])

    # OPCODE_BRANCH = 8, SUB_OPCODE_BX
    assert_decode_fields("00002080", [  # JUMP r0
        ('addr'      ,  0, ''),
        ('dreg'      ,  0, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  1, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  0, ' (--)'),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("01006080", [  # JUMP r1, EQ
        ('addr'      ,  0, ''),
        ('dreg'      ,  1, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  1, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  1, ' (EQ)'),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("0200a080", [  # JUMP r2, OV
        ('addr'      ,  0, ''),
        ('dreg'      ,  2, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  1, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  2, ' (OV)'),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("00000080", [  # JUMP 0
        ('addr'      ,  0, ''),
        ('dreg'      ,  0, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  0, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  0, ' (--)'),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("04004080", [  # JUMP 1, EQ
        ('addr'      ,  1, ''),
        ('dreg'      ,  0, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  0, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  1, ' (EQ)'),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("08008080", [  # JUMP 2, OV
        ('addr'      ,  2, ''),
        ('dreg'      ,  0, ''),
        ('opcode'    ,  8, ''),
        ('reg'       ,  0, ''),
        ('sub_opcode',  0, ''),
        ('type'      ,  2, ' (OV)'),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_BRANCH = 8, SUB_OPCODE_BR
    assert_decode_fields("01000082", [  # JUMPR 0, 1, LT
        ('cmp'       ,  0, ' (LT)'),
        ('imm'       ,  1, ''),
        ('offset'    ,  0, ''),
        ('opcode'    ,  8, ''),
        ('sign'      ,  0, ''),
        ('sub_opcode',  1, ''),
    ])
    assert_decode_fields("05000382", [  # JUMPR 1, 5, GE
        ('cmp'       ,  1, ' (GE)'),
        ('imm'       ,  5, ''),
        ('offset'    ,  1, ''),
        ('opcode'    ,  8, ''),
        ('sign'      ,  0, ''),
        ('sub_opcode',  1, ''),
    ])

    # OPCODE_BRANCH = 8, SUB_OPCODE_BS
    assert_decode_fields("01000084", [  # JUMPS 0, 1, LT
        ('cmp'       ,  0, ' (LT)'),
        ('imm'       ,  1, ''),
        ('offset'    ,  0, ''),
        ('opcode'    ,  8, ''),
        ('sign'      ,  0, ''),
        ('sub_opcode',  2, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("05800284", [  # JUMPS 1, 5, GE
        ('cmp'       ,  1, ' (GE)'),
        ('imm'       ,  5, ''),
        ('offset'    ,  1, ''),
        ('opcode'    ,  8, ''),
        ('sign'      ,  0, ''),
        ('sub_opcode',  2, ''),
        ('unused'    ,  0, ''),
    ])
    assert_decode_fields("09000584", [  # JUMPS 2, 9, LE
        ('cmp'       ,  2, ' (LE)'),
        ('imm'       ,  9, ''),
        ('offset'    ,  2, ''),
        ('opcode'    ,  8, ''),
        ('sign'      ,  0, ''),
        ('sub_opcode',  2, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_END = 9, SUB_OPCODE_END
    assert_decode_fields("01000090", [  # WAKE
        ('opcode'    ,  9, ''),
        ('sub_opcode',  0, ''),
        ('unused'    ,  0, ''),
        ('wakeup'    ,  1, ''),
    ])

    # OPCODE_END = 9, SUB_OPCODE_SLEEP
    assert_decode_fields("07000092", [  # SLEEP 7
        ('cycle_sel' ,  7, ''),
        ('opcode'    ,  9, ''),
        ('sub_opcode',  1, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_TSENS = 10
    assert_decode_fields("090000a0", [  # TSENS r0, 0
        ('delay'     ,  2, ''),
        ('dreg'      ,  1, ''),
        ('opcode'    , 10, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_HALT = 11
    assert_decode_fields("000000b0", [  # HALT
        ('opcode'    , 11, ''),
        ('unused'    ,  0, ''),
    ])

    # OPCODE_LD = 13
    assert_decode_fields("060000d0", [  # LD r2, r1, 0
        ('dreg'      ,  2, ''),
        ('offset'    ,  0, ''),
        ('opcode'    , 13, ''),
        ('sreg'      ,  1, ''),
        ('unused1'   ,  0, ''),
        ('unused2'   ,  0, ''),
    ])


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
