What is py-esp32-ulp?
---------------------

It is an assembler toolchain for the ESP32 ULP (Ultra Low-Power) Co-Processor,
written in MicroPython.

It is able to translate small, simple assembler language programs to a
loadable/executable machine code binary, at runtime, on the ESP32
microcontroller, from projects implemented in MicroPython.

This is intended as an alternative approach to assembling such programs on a
development machine using the binutils-esp32ulp toolchain from Espressif.


Status
------

The most commonly used simple stuff should work.

We have some unit tests and also compatibility tests that compare the output
whether it is identical with binutils-esp32ulp output.

There might be some stuff missing, some bugs and other symptoms of alpha
software. Also, error and exception handling is rather rough yet.

Please be patient or contribute missing parts or fixes.

See the issue tracker for known bugs and todo items.

