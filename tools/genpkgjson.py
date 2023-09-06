#
# This file is part of the micropython-esp32-ulp project,
# https://github.com/micropython/micropython-esp32-ulp
#
# SPDX-FileCopyrightText: 2018-2023, the micropython-esp32-ulp authors, see AUTHORS file.
# SPDX-License-Identifier: MIT

"""
Tool for generating package.json for the MIP package manager

Run this tool from the repo root, like:

python tools/genpkgjson.py > package.json

Note:
This tool works with both python3 and micropyton.
"""

import os
import json

PACKAGE_JSON_VERSION=1

# Update the repo when working with a fork
GITHUB_REPO="micropython/micropython-esp32-ulp"


def get_files(path):
    files = [f'{path}/{f}' for f in os.listdir(path)]
    return files


def build_urls(repo_base, files):
    return [[f, f'github:{repo_base}/{f}'] for f in files]


def print_package_json(urls):
    """
    Custom-formatting JSON output for better readability

    json.dumps in MicroPython cannot format the output and python3
    puts each element of each urls' sub-arrays onto a new line.
    Here we print each file and its source url onto the same line.
    """
    print('{')
    print(f'  "v":{PACKAGE_JSON_VERSION},')
    print('  "urls":[')
    print(',\n'.join([f'    {json.dumps(u)}' for u in sorted(urls)]))
    print('  ]')
    print('}')


if __name__ == '__main__':
    library_root = 'esp32_ulp'
    files = get_files(library_root)
    urls = build_urls(GITHUB_REPO, files)
    print_package_json(urls)
