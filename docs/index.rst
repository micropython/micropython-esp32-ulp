py-esp32-ulp Documentation
==========================

py-esp32-ulp is an assembler toolchain for the ESP32 ULP (Ultra Low-Power)
Co-Processor, written in MicroPython.

.. contents:: Table of Contents


What is it useful for?
----------------------

py-esp32-ulp can translate small assembly language programs to a
loadable/executable ULP machine code binary, directly on the ESP32
microcontroller.

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
* RTC convenience macros (e.g. WRITE_RTC_REG)
* many ESP32 ULP code examples found on the web will work unmodified


Limitations
-----------

Currently the following are not supported:

* assembler macros using ``.macro``
* preprocessor macros using ``#define A(x,y) ...``
* including files using ``#include``
* ESP32-S2 (not binary compatible with the ESP32)


Installation
------------

On the ESP32, install using upip:

.. code-block:: python

   # ensure the ESP32 is connected to a network with internet connectivity
   import upip
   upip.install('micropython-py-esp32-ulp')

On a PC, simply ``git clone`` this repo.


Getting started
---------------

On the ESP32
++++++++++++

The simplest example to try on the ESP32 is `counter.py </examples/counter.py>`_.
It shows how to assemble code, load and run the resulting binary and exchange
data between the ULP and the main CPU.

Run the ``counter.py`` example:

1. Install py-esp32-ulp onto the ESP32 as shown above
2. Upload the `examples/counter.py </examples/counter.py>`_ file to the ESP32
3. Run with ``import counter``

You can also try the `blink.py </examples/blink.py>`_ example, which shows how to
let the ULP blink an LED.

Look inside each example for a more detailed description.


On a PC
+++++++

On a PC with the unix port of MicroPython, you can assemble source code as
follows:

.. code-block:: shell

   git clone https://github.com/ThomasWaldmann/py-esp32-ulp.git
   cd py-esp32-ulp
   micropython -m esp32_ulp path/to/code.S  # this results in path/to/code.ulp


More examples
+++++++++++++

Other ULP examples from around the web:

* https://github.com/espressif/esp-iot-solution/tree/master/examples/ulp_examples
* https://github.com/duff2013/ulptool
* https://github.com/joba-1/Blink-ULP/blob/master/main/ulp/


Advanced usage
--------------

In some applications you might want to separate the assembly stage from the
loading/running stage, to avoid having to assemble the code on every startup.
This can be useful in battery-powered applications where every second of sleep
time matters.

Splitting the assembly and load stage can be combined with other techniques,
for example to implement a caching mechansim for the ULP binary that
automatically updates the binary every time the assembly source code changes.

The ``esp32_ulp.assemble_file`` function can be used to assemble and link an
assembly source file into a machine code binary file with a ``.ulp`` extension.
That file can then be loaded directly without assembling the source again.

1. Create/upload an assembly source file and run the following to get a
   loadable ULP binary as a ``.ulp`` file:

   .. code-block:: python

      import esp32_ulp
      esp32_ulp.assemble_file('code.S')  # this results in code.ulp

2. The above prints out the offsets of all global symbols/labels. For the next
   step, you will need to note down the offset of the label, which represents
   the entry point to your code.

3. Now load and run the resulting binary as follows:

   .. code-block:: python

      from esp32 import ULP

      ulp = ULP()
      with open('test.ulp', 'r') as f:
          # load the binary into RTC memory
          ulp.load_binary(0, f.read())

          # configure how often the ULP should wake up
          ulp.set_wakeup_period(0, 500000)  # 500k usec == 0.5 sec

          # start the ULP
          # assemble_file printed offsets in number of 32-bit words.
          # ulp.run() expects an offset in number of bytes.
          # Thus, multiply the offset to our entry point by 4.
          # e.g. for an offset of 2:
          #   2 words * 4 = 8 bytes
          ulp.run(2*4)  # specify the offset of the entry point label

To update the binary every time the source code changes, you would need a
mechanism to detect that the source code changed. This could trigger a re-run
of the ``assemble_file`` function to update the binary. Manually re-running
this function as needed would also work.


Preprocessor
------------

There is a simple preprocessor that understands just enough to allow assembling
ULP source files containing convenience macros such as WRITE_RTC_REG. This is
especially useful for assembling ULP examples from Espressif or other ULP code
found as part of Arduino/ESP-IDF projects.

The preprocessor and how to use it is documented here: `Preprocessor support </docs/preprocess.rst>`_.


Testing
-------

There are unit tests and also compatibility tests that check whether the binary
output is identical with what binutils-esp32ulp produces.

py-esp32-ulp has been tested on the Unix port of MicroPython and on real ESP32
devices with the chip type ESP32D0WDQ6 (revision 1) without SPIRAM.

Consult the Github Actions `workflow definition file </.github/workflows/run_tests.yaml>`_
for how to run the different tests.


Links
-----

Espressif documentation:

* `ESP32 ULP coprocessor instruction set <https://esp-idf.readthedocs.io/en/latest/api-guides/ulp_instruction_set.html>`_
* `ESP32 Technical Reference Manual <https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf>`_

GNU Assembler "as" documentation (we try to be compatible for all features that are implemented)

* `GNU Assembler manual <https://sourceware.org/binutils/docs/as/index.html>`_
