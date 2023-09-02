=====================
Disassembler
=====================

micropython-esp32-ulp contains a disassembler for disassembling code for the
ESP32 ULP (Ultra Low-Power) Co-Processor.

The main purpose of this tool is to inspect what instructions our assembler
created, what value each field is set to, and to compare this with the output
created by the assembler from Espressif (part of their `binutils-gdb fork <https://github.com/espressif/binutils-gdb/tree/esp32ulp-elf-2.35>`_),
which we use as our reference implementation.


Usage
------------------------

To disassemble a ULP binary, simply run:

.. code-block:: bash

   micropython -m tools.disassemble path/to/binary.ulp

You can also specify additional options to ``disassemble.py`` as follows:

+--------------------------+----------------------------------------------------------------+
| Option                   | Description                                                    |
+==========================+================================================================+
| ``-c`` or ``--mcpu``     | Choose ULP variant: either esp32 or esp32s2                    |
+--------------------------+----------------------------------------------------------------+
| ``-h``                   | Show help text                                                 |
+--------------------------+----------------------------------------------------------------+
|| ``-m <bytes sequence>`` || Disassemble a provided sequence of hex bytes                  |
||                         || (in this case any filename specified is ignored)              |
+--------------------------+----------------------------------------------------------------+
| ``-v``                   | Verbose mode (shows ULP header and fields of each instruction) |
+--------------------------+----------------------------------------------------------------+


Disassembling a file
------------------------

The simplest and default mode of the disassembler is to disassemble the
specified file.

Note that the ULP header is validates and files with unknown magic bytes will be
rejected. The correct 4 magic bytes at the start of a ULP binary are ``ulp\x00``.

Example disassembling an ESP32 ULP binary:

.. code-block:: shell

   $ micropython -m tools.disassemble path/to/binary.ulp
   .text
   0000  040000d0  LD r0, r1, 0
   0004  0e0000d0  LD r2, r3, 0
   0008  04000068  ST r0, r1, 0
   000c  0b000068  ST r3, r2, 0
   .data
   0010  00000000  <empty>

Example disassembling an ESP32-S2 ULP binary:

.. code-block:: shell

   $ micropython -m tools.disassemble -c esp32s2 path/to/binary.ulp
   .text
   0000  040000d0  LD r0, r1, 0
   0004  0e0000d0  LD r2, r3, 0
   0008  84010068  ST r0, r1, 0
   000c  8b010068  ST r3, r2, 0
   .data
   0010  00000000  <empty>


Disassembling a byte sequence
-----------------------------

The ``-m`` option allows disassembling a sequences hex letters representing
ULP instructions.

This option expects the actual instructions directly, without any ULP header.

The sequence must contain a number of hex letters exactly divisible by 8, i.e.
8, 16, 24, etc, because each 32-bit word is made up of 8 hex letters. Spaces
can be included in the sequence and they are ignored.

The typical use case for this feature is to copy/paste some instructions from
a hexdump (e.g. xxd output) for analysis.

Example:

.. code-block:: shell

   # hexdump binary.ulp
   $ xxd path/to/binary.ulp
   00000000: 756c 7000 0c00 2400 0400 0000 9300 8074  ulp...$........t
   00000010: 2a80 0488 2004 8074 1c00 0084 0000 0040  *... ..t.......@
   (...)

   # analyse the last 2 instructions
   $ micropython -m tools.disassemble -m "1c00 0084 0000 0040"
   0000  1c000084  JUMPS 0, 28, LT
   0004  00000040  NOP


Verbose mode
------------------------

In verbose mode the following extra outputs are enabled:

* ULP header (except when using ``-m``)
* The fields of each instruction and their values

For example:

.. code-block::

   header
   ULP magic    : b'ulp\x00' (0x00706c75)
   .text offset : 12 (0x0c)
   .text size   : 36 (0x24)
   .data offset : 48 (0x30)
   .data size   : 4 (0x04)
   .bss size    : 0 (0x00)
   ----------------------------------------
   .text
   0000  93008072  MOVE r3, 9
                    dreg       =   3
                    imm        =   9
                    opcode     =   7
                    sel        =   4 (MOV)
                    sreg       =   0
                    sub_opcode =   1
                    unused     =   0
   (...detail truncated...)
   0020  000000b0  HALT
                    opcode     =  11 (0x0b)
                    unused     =   0
   ----------------------------------------
   .data
   0000  00000000  <empty>


Disassembling on device
-----------------------------

The disassembler also works when used on an ESP32 device.

To use the disassembler on a real device:

* ensure ``micropython-esp32-ulp`` is installed on the device (see `docs/index.rst </docs/index.rst>`_).
* upload ``tools/disassemble.py`` ``tools/decode.py`` and ``tools/decode_s2.py`` to the device
  (any directory will do, as long as those 3 files are in the same directory)
* the following example code assumes you placed the 3 files into the device's "root" directory
* run the following (note, we must specify which the cpu the binary is for):

  .. code-block:: python

     from disassemble import disassemble_file
     # then either:
     disassemble_file('path/to/file.ulp', cpu='esp32s2')  # normal mode
     # or:
     disassemble_file('path/to/file.ulp', cpu='esp32s2', verbose=True)  # verbose mode
