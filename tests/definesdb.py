#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

import os

from esp32_ulp.definesdb import DefinesDB, DBNAME
from esp32_ulp.util import file_exists

tests = []


def test(param):
    tests.append(param)


@test
def test_definesdb_clear_removes_all_keys():
    db = DefinesDB()
    db.open()
    db.update({'KEY1': 'VALUE1'})

    db.clear()

    assert 'KEY1' not in db

    db.close()


@test
def test_definesdb_persists_data_across_instantiations():
    db = DefinesDB()
    db.open()
    db.clear()

    db.update({'KEY1': 'VALUE1'})

    assert 'KEY1' in db

    db.close()
    del db
    db = DefinesDB()
    db.open()

    assert db.get('KEY1', None) == 'VALUE1'

    db.close()


@test
def test_definesdb_should_not_create_a_db_file_when_only_reading():
    db = DefinesDB()

    db.clear()
    assert not file_exists(DBNAME)

    assert db.get('some-key', None) is None
    assert not file_exists(DBNAME)


if __name__ == '__main__':
    # run all methods marked with @test
    for t in tests:
        t()
