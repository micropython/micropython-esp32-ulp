import esp32_ulp.opcodes as opcodes
import ubinascii
import sys


def decode_instruction(i):
    ins = opcodes._end
    ins.all = i  # abuse a struct to get opcode and sub_opcode

    print(ubinascii.hexlify(i.to_bytes(4, 'little')))

    if ins.opcode == opcodes.OPCODE_ADC:
        print('OPCODE_ADC')
        opcodes._adc.all = i
        ins = opcodes._adc
    elif ins.opcode == opcodes.OPCODE_ALU and ins.sub_opcode == opcodes.SUB_OPCODE_ALU_CNT:
        print('OPCODE_ALU / SUB_OPCODE_ALU_CNT')
        opcodes._alu_cnt.all = i
        ins = opcodes._alu_cnt
    elif ins.opcode == opcodes.OPCODE_ALU and ins.sub_opcode == opcodes.SUB_OPCODE_ALU_IMM:
        print('OPCODE_ALU / SUB_OPCODE_ALU_IMM')
        opcodes._alu_imm.all = i
        ins = opcodes._alu_imm
    elif ins.opcode == opcodes.OPCODE_ALU and ins.sub_opcode == opcodes.SUB_OPCODE_ALU_REG:
        print('OPCODE_ALU / SUB_OPCODE_ALU_REG')
        opcodes._alu_reg.all = i
        ins = opcodes._alu_reg
    elif ins.opcode == opcodes.OPCODE_BRANCH and ins.sub_opcode == opcodes.SUB_OPCODE_BX:
        print('JUMP')
        opcodes._bx.all = i
        ins = opcodes._bx
    elif ins.opcode == opcodes.OPCODE_BRANCH and ins.sub_opcode == opcodes.SUB_OPCODE_BR:
        print('JUMPR')
        opcodes._br.all = i
        ins = opcodes._br
    elif ins.opcode == opcodes.OPCODE_BRANCH and ins.sub_opcode == opcodes.SUB_OPCODE_BS:
        print('JUMPS')
        opcodes._bs.all = i
        ins = opcodes._bs
    elif ins.opcode == opcodes.OPCODE_DELAY:
        print('OPCODE_DELAY')
        opcodes._delay.all = i
        ins = opcodes._delay
    elif ins.opcode == opcodes.OPCODE_END and ins.sub_opcode == opcodes.SUB_OPCODE_END:
        print('OPCODE_END')
        opcodes._end.all = i
        ins = opcodes._end
    elif ins.opcode == opcodes.OPCODE_END and ins.sub_opcode == opcodes.SUB_OPCODE_SLEEP:
        print('OPCODE_SLEEP')
        opcodes._sleep.all = i
        ins = opcodes._sleep
    elif ins.opcode == opcodes.OPCODE_HALT:
        print('OPCODE_HALT')
        opcodes._halt.all = i
        ins = opcodes._halt
    elif ins.opcode == opcodes.OPCODE_I2C:
        print('OPCODE_I2C')
        opcodes._i2c.all = i
        ins = opcodes._i2c
    elif ins.opcode == opcodes.OPCODE_LD:
        print('OPCODE_LD')
        opcodes._ld.all = i
        ins = opcodes._ld
    elif ins.opcode == opcodes.OPCODE_RD_REG:
        print('OPCODE_RD_REG')
        opcodes._rd_reg.all = i
        ins = opcodes._rd_reg
    elif ins.opcode == opcodes.OPCODE_ST:
        print('OPCODE_ST')
        opcodes._st.all = i
        ins = opcodes._st
    elif ins.opcode == opcodes.OPCODE_TSENS:
        print('OPCODE_TSENS')
        opcodes._tsens.all = i
        ins = opcodes._tsens
    elif ins.opcode == opcodes.OPCODE_WR_REG:
        print('OPCODE_WR_REG')
        opcodes._wr_reg.all = i
        ins = opcodes._wr_reg

    possible_fields = (
        'addr', 'cmp', 'cycle_sel', 'cycles', 'data', 'delay', 'dreg',
        'high', 'i2c_sel', 'imm', 'low', 'mux', 'offset', 'opcode',
        'periph_sel', 'reg', 'rw', 'sar_sel', 'sel', 'sign', 'sreg',
        'sub_addr', 'sub_opcode', 'treg', 'type', 'unused', 'unused1',
        'unused2', 'wakeup'
    )
    for field in possible_fields:
        try:
            # eval is ugly but constrained to possible_fields and variable ins
            val = eval('i.%s' % field, {}, {'i': ins})
        except KeyError:
            continue
        extra = ''
        if field == 'sel':
            if ins.sub_opcode == opcodes.SUB_OPCODE_ALU_CNT:
                alu_ops = ('INC', 'DEC', 'RST')
            else:
                alu_ops = ('ADD', 'SUB', 'AND', 'OR', 'MOV', 'LSH', 'RSH')
            extra = ' (%s)' % alu_ops[val]
        elif field == 'cmp':
            cmp_ops = ('LT', 'GE', 'LE', 'EQ', 'GT')
            extra = ' (%s)' % cmp_ops[val]
        print("  {:10} = {:3}{}".format(field, val, extra))


def disassemble_manually(byte_sequence_string):
    sequence = byte_sequence_string.strip().replace(' ','')
    chars_per_instruction = 8
    list = [
        sequence[i:i+chars_per_instruction]
        for i in range(0, len(sequence), chars_per_instruction)
    ]

    for instruction in list:
        byte_sequence = ubinascii.unhexlify(instruction.replace(' ',''))
        i = int.from_bytes(byte_sequence, 'little')
        decode_instruction(i)


def handle_cmdline(params):
    byte_sequence = "".join(params)
    disassemble_manually(byte_sequence)


if sys.argv: # if run from cmdline
    handle_cmdline(sys.argv[1:])
