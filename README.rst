.. start-badges

.. image:: ../../actions/workflows/run_tests.yaml/badge.svg
   :height: 20px
   :target: ../../actions/workflows/run_tests.yaml
   :alt: Build Status

.. end-badges

=====================
py-esp32-ulp
=====================

py-esp32-ulp is an assembler toolchain for the ESP32 ULP (Ultra Low-Power)
Co-Processor, written in MicroPython.

It can translate small assembly language programs to a loadable/executable
ULP machine code binary, directly on the ESP32 microcontroller.

This is intended as an alternative approach to assembling such programs using
the binutils-esp32ulp toolchain from Espressif on a development machine.

It can also be useful in cases where binutils-esp32ulp is not available.


Features
--------

The following features are supported:

* the entire `ESP32 ULP instruction set <https://esp-idf.readthedocs.io/en/latest/api-guides/ulp_instruction_set.html>`_
* constants defined with ``.set``
* constants defined with ``#define``
* expressions in assembly code and constant definitions
* RTC convenience macros (e.g. ``WRITE_RTC_REG``)
* many ESP32 ULP code examples found on the web will work unmodified


Quick start
-----------

To get going run the following directly on the ESP32:

.. code-block:: python

   # Step 1: Install py-esp32-ulp
   # IMPORTANT: Ensure the ESP32 is connected to a network with internet connectivity.
   import upip
   upip.install('micropython-py-esp32-ulp')

   # Step 2: Run an example
   # First, upload examples/counter.py to the ESP32.
   import counter

The `examples/counter.py </examples/counter.py>`_ example shows how to assemble code,
load and run the resulting binary and exchange data between the ULP and the main CPU.


Documentation
-------------
See `docs/index.rst </docs/index.rst>`_.


Requirements
------------

The minimum supported version of MicroPython is v1.12.

An ESP32 is required to run the ULP machine code binary produced by py-esp32-ulp
(the ESP32-S2 will not work as it is not binary compatible with the ESP32).


License
-------

This project is released under the `MIT License </LICENSE>`_.

