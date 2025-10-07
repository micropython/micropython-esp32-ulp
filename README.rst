.. start-badges

.. image:: ../../actions/workflows/run_tests.yaml/badge.svg
   :height: 20px
   :target: ../../actions/workflows/run_tests.yaml
   :alt: Build Status

.. end-badges

=====================
micropython-esp32-ulp
=====================

micropython-esp32-ulp is an assembler toolchain for the ESP32 ULP (Ultra Low-Power)
Co-Processor, written in MicroPython.

It can translate small assembly language programs to a loadable/executable
ULP-FSM (not RISC-V) machine code binary, directly on an ESP32 microcontroller.

This is intended as an alternative approach to assembling such programs using
the `binutils-gdb toolchain <https://github.com/espressif/binutils-gdb/tree/esp32ulp-elf-2.35>`_
(esp32-elf-as) from Espressif on a development machine.

It can also be useful in cases where esp32-elf-as is not available.


Features
--------

The following features are supported:

* the entire `ESP32 ULP instruction set <https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ulp_instruction_set.html>`_
* the entire `ESP32-S2 ULP instruction set <https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/api-reference/system/ulp_instruction_set.html>`_
  (this also covers the ESP32-S3) [#f1]_ [#f2]_
* constants defined with ``.set``
* constants defined with ``#define``
* expressions in assembly code and constant definitions
* RTC convenience macros (e.g. ``WRITE_RTC_REG``)
* many ESP32 ULP code examples found on the web will work unmodified
* a simple disassembler is also provided

.. [#f1] Note: the ESP32-S2 and ESP32-S3 have the same ULP binary format,
         but the binary format is different from that of the original ESP32 ULP. You need to
         select the ``esp32s2`` CPU (`see docs </docs/index.rst>`_) when assembling code for
         use on an ESP32-S2/S3.

.. [#f2] Note: The ESP32-S2 and ESP32-S3 have the same ULP binary format, but the peripheral
         register addresses (those accessed with REG_RD and REG_WR) are different. For best
         results, use the correct peripheral register addresses for the specific variant you
         are working with. The assembler (when used with ``cpu=esp32s2``) will accept
         addresses for any of the 3 variants, because they are translated into relative
         offsets anyway, and many registers live at the same relative offset on all 3 variants.
         This conveniently means that the same assembly code can be assembled unmodified for each
         variant and produce a correctly working binary - as long as only peripheral registers
         are used, which have the same relative offset across the variants. Use with care!


Quick start
-----------

To get going, run the following directly on the ESP32:

.. code-block:: python

   # IMPORTANT: Ensure the ESP32 is connected to a network with internet connectivity.

   # Step 1: Install micropython-esp32-ulp (for MicroPython v1.20 or newer)
   import mip
   mip.install('github:micropython/micropython-esp32-ulp')

   # Step 1: Install micropython-esp32-ulp (for MicroPython older than v1.20)
   import upip
   upip.install('micropython-esp32-ulp')

   # Step 2: Run an example
   # First, upload examples/counter.py to the ESP32.
   import counter

The `examples/counter.py </examples/counter.py>`_ example shows how to assemble code,
load and run the resulting binary, and exchange data between the ULP and the main CPU.


Documentation
-------------
See `docs/index.rst </docs/index.rst>`_.


Requirements
------------

The minimum supported version of MicroPython is v1.12. (For ESP32-S2 and ESP32-S3
devices, a version greater than v1.20 is required, as earlier versions did not
enable the ``esp32.ULP`` class).

An ESP32 device is required to run the ULP machine code binary produced by
micropython-esp32-ulp.


License
-------

This project is released under the `MIT License </LICENSE>`_.

