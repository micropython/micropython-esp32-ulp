#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

import sys

from .preprocess import Preprocessor
from .definesdb import DefinesDB


def parse(files):
    db = DefinesDB()

    p = Preprocessor()
    p.use_db(db)

    for f in files:
        print('Processing file:', f)

        p.process_include_file(f)

    print('Done.')


if __name__ == '__main__':
    parse(sys.argv[1:])

