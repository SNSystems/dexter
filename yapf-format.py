#!/usr/bin/env python

# DExTer : Debugging Experience Tester
# ~~~~~~   ~         ~~         ~   ~~
#
# Copyright (c) 2018 by SN Systems Ltd., Sony Interactive Entertainment Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Run YAPF (Yet Another Python Formatter) across the DExTer codebase.
See https://github.com/google/yapf
"""

import os
import sys

try:
    from yapf.yapflib.yapf_api import FormatFile
except ImportError as e:
    sys.stderr.write('\n{}\ntry: "{}" -m pip install yapf\n\n'.format(
        e, sys.executable))
    raise

if __name__ == '__main__':  # noqa
    dexter_dir = os.path.dirname(os.path.abspath(__file__))
    style_config = os.path.join(dexter_dir, 'setup.cfg')

    changed_files = []
    errors = []

    for r, _, fs in os.walk(dexter_dir):

        if any(d in r for d in ('.git', 'thirdparty')):
            continue

        for f in fs:
            if not f.endswith('.py'):
                continue

            path = os.path.join(r, f)

            try:
                _, _, changed = FormatFile(
                    path, in_place=True, style_config=style_config)
            except SyntaxError as e:
                errors.append('{}({}): {}'.format(path, e.lineno, e.msg))
                sys.stdout.write('E')
                sys.stdout.flush()
                continue

            if changed:
                changed_files.append(path)
                sys.stdout.write('C')
            else:
                sys.stdout.write('.')
                sys.stdout.flush()

    sys.stdout.write('\n')

    if changed_files:
        print('\n{} file{} reformatted:\n  * {}'.format(
            len(changed_files), ''
            if len(changed_files) == 1 else 's', '\n  * '.join(changed_files)))
    else:
        print('\nno files reformatted.')

    if errors:
        print('\n{} file{} had errors:\n  * {}\n'.format(
            len(errors), ''
            if len(errors) == 1 else 's', '\n  * '.join(errors)))
    else:
        print('\nOK')
