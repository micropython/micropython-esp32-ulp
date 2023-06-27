from uctypes import struct, addressof, LITTLE_ENDIAN, UINT16, UINT32
from esp32_ulp.opcodes import RD_REG_PERIPH_RTC_CNTL, RD_REG_PERIPH_RTC_IO, RD_REG_PERIPH_RTC_I2C, \
    RD_REG_PERIPH_SENS, DR_REG_MAX_DIRECT
import esp32_ulp.opcodes as opcodes
import esp32_ulp.soc as soc
import ubinascii
import sys


alu_cnt_ops = ('STAGE_INC', 'STAGE_DEC', 'STAGE_RST')
alu_ops = ('ADD', 'SUB', 'AND', 'OR', 'MOVE', 'LSH', 'RSH')
jump_types = ('--', 'EQ', 'OV')
cmp_ops = ('LT', 'GE', 'LE', 'EQ', 'GT')

lookup = {
    opcodes.OPCODE_ADC: ('ADC', opcodes._adc, lambda op: 'ADC r%s, %s, %s' % (op.dreg, op.mux, op.sar_sel)),
    opcodes.OPCODE_ALU: ('ALU', opcodes._alu_imm, {
        opcodes.SUB_OPCODE_ALU_CNT: (
            'ALU_CNT',
            opcodes._alu_cnt,
            lambda op: '%s%s' % (alu_cnt_ops[op.sel], '' if op.sel == opcodes.ALU_SEL_RST else ' %s' % op.imm)
        ),
        opcodes.SUB_OPCODE_ALU_IMM: (
            'ALU_IMM',
            opcodes._alu_imm,
            lambda op: '%s r%s, %s' % (alu_ops[op.sel], op.dreg, op.imm) if op.sel == opcodes.ALU_SEL_MOV
                else '%s r%s, r%s, %s' % (alu_ops[op.sel], op.dreg, op.sreg, op.imm)
        ),
        opcodes.SUB_OPCODE_ALU_REG: (
            'ALU_REG',
            opcodes._alu_reg,
            lambda op: '%s r%s, r%s' % (alu_ops[op.sel], op.dreg, op.sreg) if op.sel == opcodes.ALU_SEL_MOV
                else '%s r%s, r%s, r%s' % (alu_ops[op.sel], op.dreg, op.sreg, op.treg)
        ),
    }),
    opcodes.OPCODE_BRANCH: ('BRANCH', opcodes._bx, {
        opcodes.SUB_OPCODE_BX: (
            'BX',
            opcodes._bx,
            lambda op: 'JUMP %s%s' % (op.addr if op.reg == 0 else 'r%s' % op.dreg, ', %s' % jump_types[op.type]
                if op.type != 0 else '')
        ),
        opcodes.SUB_OPCODE_BR: (
            'BR',
            opcodes._br,
            lambda op: 'JUMPR %s, %s, %s' % ('%s%s' % ('-' if op.sign == 1 else '', op.offset), op.imm, cmp_ops[op.cmp])
        ),
        opcodes.SUB_OPCODE_BS: (
            'BS',
            opcodes._bs,
            lambda op: 'JUMPS %s, %s, %s' % ('%s%s' % ('-' if op.sign == 1 else '', op.offset), op.imm, cmp_ops[op.cmp])
        ),
    }),
    opcodes.OPCODE_DELAY: (
        'DELAY',
        opcodes._delay,
        lambda op: 'NOP' if op.cycles == 0 else 'WAIT %s' % op.cycles
    ),
    opcodes.OPCODE_END: ('END', opcodes._end, {
        opcodes.SUB_OPCODE_END: (
            'WAKE',
            opcodes._end
        ),
        opcodes.SUB_OPCODE_SLEEP: (
            'SLEEP',
            opcodes._sleep,
            lambda op: 'SLEEP %s' % op.cycle_sel
        ),
    }),
    opcodes.OPCODE_HALT: ('HALT', opcodes._halt),
    opcodes.OPCODE_I2C: (
        'I2C',
        opcodes._i2c,
        lambda op: 'I2C_%s %s, %s, %s, %s' % ('RD' if op.rw == 0 else 'WR', op.sub_addr, op.high, op.low, op.i2c_sel)
    ),
    opcodes.OPCODE_LD: ('LD', opcodes._ld, lambda op: 'LD r%s, r%s, %s' % (op.dreg, op.sreg, op.offset)),
    opcodes.OPCODE_ST: ('ST', opcodes._st, lambda op: 'ST r%s, r%s, %s' % (op.sreg, op.dreg, op.offset)),
    opcodes.OPCODE_RD_REG: (
        'RD_REG',
        opcodes._rd_reg,
        lambda op: 'REG_RD 0x%x, %s, %s' % (op.periph_sel << 8 | op.addr, op.high, op.low)
    ),
    opcodes.OPCODE_WR_REG: (
        'WR_REG',
        opcodes._wr_reg,
        lambda op: 'REG_WR 0x%x, %s, %s, %s' % (op.periph_sel << 8 | op.addr, op.high, op.low, op.data)
    ),
    opcodes.OPCODE_TSENS: ('TSENS', opcodes._tsens, lambda op: 'TSENS r%s, %s' % (op.dreg, op.delay)),
}


def decode_instruction(i):
    if i == 0:
        raise Exception('<empty>')

    ins = opcodes._end
    ins.all = i  # abuse a struct to get opcode

    params = lookup.get(ins.opcode, None)

    if not params:
        raise Exception('Unknown instruction')

    if len(params) == 3:
        name, ins, third = params
        ins.all = i

        if callable(third):
            params = (third(ins), ins)
        else:
            params = third.get(ins.sub_opcode, ())

    if len(params) == 3:
        name, ins, pretty = params
        ins.all = i
        name = pretty(ins)
    else:
        name, ins = params
        ins.all = i

    return ins, name


def get_instruction_fields(ins):
    possible_fields = (
        'addr', 'cmp', 'cycle_sel', 'cycles', 'data', 'delay', 'dreg',
        'high', 'i2c_sel', 'imm', 'low', 'mux', 'offset', 'opcode',
        'periph_sel', 'reg', 'rw', 'sar_sel', 'sel', 'sign', 'sreg',
        'sub_addr', 'sub_opcode', 'treg', 'type', 'unused', 'unused1',
        'unused2', 'wakeup'
    )
    field_details = []
    for field in possible_fields:
        extra = ''
        try:
            # eval is ugly but constrained to possible_fields and variable ins
            val = eval('i.%s' % field, {}, {'i': ins})
            if (val>9):
                extra = ' (0x%02x)' % val
        except KeyError:
            continue

        if field == 'sel':  # ALU
            if ins.sub_opcode == opcodes.SUB_OPCODE_ALU_CNT:
                extra = ' (%s)' % alu_cnt_ops[val]
            else:
                extra = ' (%s)' % alu_ops[val]
        elif field == 'type':  # JUMP
            extra = ' (%s)' % jump_types[val]
        elif field == 'cmp':  # JUMPR/JUMPS
            extra = ' (%s)' % cmp_ops[val]

        field_details.append((field, val, extra))

    return field_details


def chunk_into_words(code, bytes_per_word, byteorder):
    chunks = [
        ubinascii.hexlify(code[i:i + bytes_per_word])
        for i in range(0, len(code), bytes_per_word)
    ]

    words = [int.from_bytes(ubinascii.unhexlify(i), byteorder) for i in chunks]

    return words


def print_ulp_header(h):
    print('header')
    print('ULP magic    : %s (0x%08x)' % (h.magic.to_bytes(4, 'little'), h.magic))
    print('.text offset : %s (0x%02x)' % (h.text_offset, h.text_offset))
    print('.text size   : %s (0x%02x)' % (h.text_size, h.text_size))
    print('.data offset : %s (0x%02x)' % (h.text_offset+h.text_size, h.text_offset+h.text_size))
    print('.data size   : %s (0x%02x)' % (h.data_size, h.data_size))
    print('.bss size    : %s (0x%02x)' % (h.bss_size, h.bss_size))
    print('----------------------------------------')


def print_code_line(byte_offset, i, asm):
    lineformat = '{0:04x}  {1}  {2}'
    hex = ubinascii.hexlify(i.to_bytes(4, 'little'))
    print(lineformat.format(byte_offset, hex.decode('utf-8'), asm))


def decode_instruction_and_print(byte_offset, i, verbose=False):
    try:
        ins, name = decode_instruction(i)
    except Exception as e:
        print_code_line(byte_offset, i, e)
        return

    print_code_line(byte_offset, i, name)

    if verbose:
        for field, val, extra in get_instruction_fields(ins):
            print("                 {:10} = {:3}{}".format(field, val, extra))


def print_text_section(code, verbose=False):
    print('.text')

    words = chunk_into_words(code, bytes_per_word=4, byteorder='little')

    for idx, i in enumerate(words):
        decode_instruction_and_print(idx << 2,i , verbose)


def print_data_section(data_offset, code):
    print('.data')

    words = chunk_into_words(code, bytes_per_word=4, byteorder='little')

    for idx, i in enumerate(words):
        asm = "<empty>" if i == 0 else "<non-empty>"
        print_code_line(data_offset + (idx << 2), i, asm)


def disassemble_manually(byte_sequence_string, verbose=False):
    sequence = byte_sequence_string.strip().replace(' ','')
    chars_per_instruction = 8
    list = [
        sequence[i:i+chars_per_instruction]
        for i in range(0, len(sequence), chars_per_instruction)
    ]

    for idx, instruction in enumerate(list):
        byte_sequence = ubinascii.unhexlify(instruction.replace(' ',''))
        i = int.from_bytes(byte_sequence, 'little')
        decode_instruction_and_print(idx << 2, i, verbose)


def disassemble_file(filename, verbose=False):
    with open(filename, 'rb') as f:
        data = f.read()

    binary_header_struct_def = dict(
        magic = 0 | UINT32,
        text_offset = 4 | UINT16,
        text_size = 6 | UINT16,
        data_size = 8 | UINT16,
        bss_size = 10 | UINT16,
    )
    h = struct(addressof(data), binary_header_struct_def, LITTLE_ENDIAN)

    if (h.magic != 0x00706c75):
        print('Invalid signature: 0x%08x (should be: 0x%08x)' % (h.magic, 0x00706c75))
        return

    if verbose:
        print_ulp_header(h)

    code = data[h.text_offset:(h.text_offset+h.text_size)]
    print_text_section(code, verbose)

    if verbose:
        print('----------------------------------------')

    data_offset = h.text_offset+h.text_size
    code = data[data_offset:(data_offset+h.data_size)]
    print_data_section(data_offset-h.text_offset, code)


def print_help():
    print('Usage: disassemble.py [<options>] [-m <byte_sequence> | <filename>]')
    print('')
    print('Options:')
    print('  -h                  Show this help text')
    print('  -m <byte_sequence>  Sequence of hex bytes (8 per instruction)')
    print('  -v                  Verbose mode. Show ULP header and fields of each instruction')
    print('  <filename>          Path to ULP binary')
    pass


def handle_cmdline(params):
    verbose = False
    filename = None
    byte_sequence = None

    while params:
        if params[0] == '-h':
            print_help()
            sys.exit(0)
        elif params[0] == '-m':
            if len(params) == 1:
                print_help()
                sys.exit(1)
            params = params[1:] # remove -m from list

            sequence_len = len(params)
            for i in range(0, len(params)):
                if params[i][0] == '-':  # start of a next option
                    sequence_len = i-1
                    break

            if sequence_len < 0:
                print_help()
                sys.exit(1)

            byte_sequence = "".join(params[:sequence_len+1])
            params = params[sequence_len:]
        elif params[0] == '-v':
            verbose = True
        elif params[0][0] == '-':
            # ignore unknown options for now
            pass
        else:
            if not filename:
                filename = params[0]

        params = params[1:]  # remove first param from list

    if byte_sequence:
        disassemble_manually(byte_sequence, verbose)
    elif filename:
        disassemble_file(filename, verbose)


if sys.argv: # if run from cmdline
    handle_cmdline(sys.argv[1:])
