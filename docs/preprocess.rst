=====================
Preprocessor
=====================

py-esp32-ulp contains a small preprocessor, which aims to fulfill one goal:
facilitate assembling of ULP code from Espressif and other open-source
projects to loadable/executable machine code without modification.

Such code uses convenience macros (``READ_RTC_*`` and ``WRITE_RTC_*``)
provided by the ESP-IDF framework, along with constants defined in the
framework's include files (such as ``RTC_GPIO_IN_REG``), to make reading
and writing from/to peripheral registers much easier.

In order to do this the preprocessor has two capabilities:

1. Parse and replace identifiers defined with ``#define``
2. Recognise the ``WRITE_RTC_*`` and ``READ_RTC_*`` macros and expand
   them in a way that mirrors what the real ESP-IDF macros do.


Usage
------------------------

Normally the assembler is called as follows

.. code-block:: python

    src = "..full assembler file contents"
    assembler = Assembler()
    assembler.assemble(src)
    ...

With the preprocessor, simply pass the source code via the preprocessor first:

.. code-block:: python

    from preprocess import preprocess

    src = "..full assembler file contents"
    src = preprocess(src)
    assembler = Assembler()
    assembler.assemble(src)
    ...


Using a "Defines Database"
--------------------------

Because the py-esp32-ulp assembler was built for running on the ESP32
microcontroller with limited RAM, the preprocessor aims to work there too.

To handle large number of defined constants (such as the ``RTC_*`` constants from
the ESP-IDF) the preprocessor can use a database (based on BerkleyDB) stored on the
device's filesystem for looking up defines.

The database needs to be populated before preprocessing. (Usually, when only using
constants from the ESP-IDF, this is a one-time step, because the include files
don't change.) The database can be reused for all subsequent preprocessor runs.

(The database can also be generated on a PC and then deployed to the ESP32, to
save processing effort on the device. In that case the include files themselves
are not needed on the device either.)

1. Build the defines database

   The ``esp32_ulp.parse_to_db`` tool can be used to generate the defines
   database from include files. The resulting file will be called
   ``defines.db``.

   (The following assume running on a PC. To do this on device, refer to the
   `esp32_ulp/parse_to_db.py <../esp32_ulp/parse_to_db.py>`_ file.)

   .. code-block:: bash

      # general command
      micropython -m esp32_ulp.parse_to_db path/to/include.h

      # loading specific ESP-IDF include files
      micropython -m esp32_ulp.parse_to_db esp-idf/components/soc/esp32/include/soc/soc_ulp.h

      # loading multiple files at once
      micropython -m esp32_ulp.parse_to_db esp-idf/components/soc/esp32/include/soc/*.h

      # if file system space is not a concern, the following can be convenient
      # by including all relevant include files from the ESP-IDF framework.
      # This results in an approximately 2MB large database.
      micropython -m esp32_ulp.parse_to_db \
        esp-idf/components/soc/esp32/include/soc/*.h \
        esp-idf/components/esp_common/include/*.h

      # most ULP code uses only 5 include files. Parsing only those into the
      # database should thus allow assembling virtually all ULP code one would
      # find or want to write.
      # This results in an approximately 250kB large database.
      micropython -m esp32_ulp.parse_to_db \
        esp-idf/components/soc/esp32/include/soc/{soc,soc_ulp,rtc_cntl_reg,rtc_io_reg,sens_reg}.h

2. Using the defines database during preprocessing

   The preprocessor will automatically use a defines database, when using the
   ``preprocess.preprocess`` convenience function, even when the database does
   not exist (an absent database is treated like an empty database, and care
   is taken not to create an empty database file, cluttering up the filesystem,
   when not needed).

   If you do not want the preprocessor use use a DefinesDB, pass ``False`` to
   the ``use_defines_db`` argument of the ``preprocess`` convenience function,
   or instantiate the ``Preprocessor`` class directly, without passing it a
   DefinesDB instance via ``use_db``.

Design choices
--------------

The preprocessor does not support:

1. Function style macros such as :code:`#define f(a,b) (a+b)`

   This is not important, because there are only few RTC macros that need
   to be supported and they are simply implemented as Python functions.

   Since the preprocessor will understand ``#define`` directives directly in the
   assembler source file, include mechanisms are not needed in some cases
   (simply copying the needed ``#define`` statements from include files into the
   assembler source will work).

2. ``#include`` directives

   The preprocessor does not currently follow ``#include`` directives. To
   limit space requirements (both in memory and on the filesystem), the
   preprocessor relies on a database of defines (key/value pairs). This
   database should be populated before using the preprocessor, by using the
   ``esp32_ulp.parse_to_db`` tool (see section above), which parses include
   files for identifiers defined therein.

3. Preserving comments

   The assumption is that the output will almost always go into the
   assembler directly, so preserving comments is not very useful and
   would add a lot of complexity.
