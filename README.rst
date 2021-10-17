=====================
py-esp32-ulp
=====================

.. image:: ../../actions/workflows/run_tests.yaml/badge.svg
   :height: 20px
   :target: ../../actions/workflows/run_tests.yaml
   :alt: Build Status

py-esp32-ulp is an assembler toolchain for the ESP32 ULP (Ultra Low-Power)
Co-Processor, written in MicroPython.

It can translate small assembly language programs to a loadable/executable
ULP machine code binary, directly on the ESP32 microcontroller.

This is intended as an alternative approach to assembling such programs using
the binutils-esp32ulp toolchain from Espressif on a development machine.


Installation
------------

On the ESP32, install using upip:

.. code-block:: python

   # ensure the ESP32 is connected to a network with internet connectivity
   import upip
   upip.install('micropython-py-esp32-ulp')

On a PC, simply ``git clone`` this repo.


Getting Started
---------------

The quickest way to get started is to try one of the `examples <examples/>`_.

The simplest example is `counter.py <examples/counter.py>`_. It shows how to
assemble code, load and run the resulting binary and exchange data between the
ULP and the main CPU.

Run the ``counter.py`` example:

1. Install py-esp32-ulp onto the ESP32 as shown above
2. Upload the `counter.py <examples/counter.py>`_ file to the ESP32
3. Run with ``import counter``

You can also try the `blink.py <examples/blink.py>`_ example, which shows how to
let the ULP blink an LED.

Look inside each example for a more detailed description.


Support
-------

The following features are supported:

* The entire `ESP32 ULP instruction set <https://esp-idf.readthedocs.io/en/latest/api-guides/ulp_instruction_set.html>`_
* Constants defined with ``.set``
* Constants defined with ``#define``
* Expressions in assembly code and constant definitions
* RTC convenience macros (e.g. WRITE_RTC_REG)
* Many ESP32 ULP code examples found on the web will work unmodified

Not currently supported:

* Assembler macros using ``.macro``
* Preprocessor macros using ``#define A(x,y) ...``
* Including files using ``#include``
* ESP32-S2 (not binary compatible with the ESP32)


Requirements
------------

The minimum supported version of MicroPython is v1.12.

py-esp32-ulp has been tested on the Unix port of MicroPython and on real ESP32
devices with the chip type ESP32D0WDQ6 (revision 1) without SPIRAM.


Advanced usage
--------------

In real world applications, you might want to separate the assembly stage from
the loading/running stage, to avoid having to assemble the code on every startup.

The ``esp32_ulp.assemble_file`` function stores the assembled and linked binary
into a file with a ``.ulp`` extension, which can later be loaded directly without
assembling the source again.

1. Create/upload an assembly source file and run the following to get a loadable
   ULP binary as a ``.ulp`` file:

   .. code-block:: python

      import esp32_ulp
      esp32_ulp.assemble_file('code.S')  # this results in code.ulp

   Alternatively you can assemble the source on a PC with MicroPython, and transfer
   the resulting ULP binary to the ESP32.

   .. code-block:: python

      git clone https://github.com/ThomasWaldmann/py-esp32-ulp
      cd py-esp32-ulp
      micropython -m esp32_ulp path/to/code.S  # this results in path/to/code.ulp
      # now upload path/to/code.ulp to the ESP32

2. The above prints out the offsets of all global symbols/labels. For the next step,
   you will need to note down the offset of the label, which represents the entry
   point to your code.

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


Preprocessor
------------

There is a simple preprocessor that understands just enough to allow assembling
ULP source files containing convenience macros such as WRITE_RTC_REG. This is
especially useful for assembling ULP examples from Espressif or other ULP code
found as part of Arduino/ESP-IDF projects.

The preprocessor and how to use it is documented here: `Preprocessor support <docs/preprocess.rst>`_.


Testing
-------

There are unit tests and also compatibility tests that check whether the binary
output is identical with what binutils-esp32ulp produces.

Consult the Github Actions `workflow definition file <.github/workflows/run_tests.yaml>`_
for how to run the different tests.


Links
-----

Espressif documentation:

* `ESP32 ULP coprocessor instruction set <https://esp-idf.readthedocs.io/en/latest/api-guides/ulp_instruction_set.html>`_
* `ESP32 Technical Reference Manual <https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf>`_

GNU Assembler "as" documentation (we try to be compatible for all features that are implemented)

* `GNU Assembler manual <https://sourceware.org/binutils/docs/as/index.html>`_

More ULP examples:

* https://github.com/espressif/esp-iot-solution/tree/master/examples/ulp_examples
* https://github.com/duff2013/ulptool
* https://github.com/joba-1/Blink-ULP/blob/master/main/ulp/


License
-------

This project is released under the `MIT License <LICENSE>`_.
