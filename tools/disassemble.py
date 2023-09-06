#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

from uctypes import struct, addressof, LITTLE_ENDIAN, UINT16, UINT32
import ubinascii
import sys


# placeholders:
# these functions will be dynamically loaded later based on the chosen cpu
decode_instruction, get_instruction_fields = None, None


def load_decoder(cpu):
    if cpu == 'esp32':
        mod = 'decode'
    elif cpu == 'esp32s2':
        mod = 'decode_s2'
    else:
        raise ValueError('Invalid cpu')

    relative_import = 1 if '/' in __file__ else 0
    decode = __import__(mod, globals(), locals(), [], relative_import)

    global decode_instruction, get_instruction_fields
    decode_instruction = decode.decode_instruction
    get_instruction_fields = decode.get_instruction_fields


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


def disassemble_manually(byte_sequence_string, cpu, verbose=False):
    load_decoder(cpu)

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


def disassemble_file(filename, cpu, verbose=False):
    load_decoder(cpu)

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
    print('  -c                  Choose ULP variant: either esp32 or esp32s2')
    print('  -h                  Show this help text')
    print('  -m <byte_sequence>  Sequence of hex bytes (8 per instruction)')
    print('  -v                  Verbose mode. Show ULP header and fields of each instruction')
    print('  <filename>          Path to ULP binary')
    pass


def handle_cmdline(params):
    cpu = 'esp32'
    verbose = False
    filename = None
    byte_sequence = None

    while params:
        if params[0] == '-h':
            print_help()
            sys.exit(0)
        elif params[0] == '-c':
            cpu = params[1]
            params = params[1:]  # remove first param from list
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
        disassemble_manually(byte_sequence, cpu, verbose)
    elif filename:
        disassemble_file(filename, cpu, verbose)


if sys.argv: # if run from cmdline
    handle_cmdline(sys.argv[1:])
