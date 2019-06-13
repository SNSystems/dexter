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
"""Unit test harness."""

from fnmatch import fnmatch
import os
import unittest

from io import StringIO

from dex.utils import is_native_windows, has_pywin32
from dex.utils import PreserveAutoColors, PrettyOutput
from dex.utils import Timer


class DexTestLoader(unittest.TestLoader):
    def _match_path(self, path, full_path, pattern):
        """Don't try to import platform-specific modules for the wrong platform
        during test discovery.
        """
        d = os.path.basename(os.path.dirname(full_path))
        if is_native_windows():
            if d == 'posix':
                return False
            if d == 'windows':
                return has_pywin32()
        else:
            if d == 'windows':
                return False
        return fnmatch(path, pattern)


def unit_tests_ok(context):
    unittest.TestCase.maxDiff = None  # remove size limit from diff output.

    with Timer('unit tests'):
        suite = DexTestLoader().discover(
            context.root_directory, pattern='*.py')
        stream = StringIO()
        result = unittest.TextTestRunner(verbosity=2, stream=stream).run(suite)

        ok = result.wasSuccessful()
        if not ok or context.options.unittest == 'show-all':
            with PreserveAutoColors(context.o):
                context.o.auto_reds.extend(
                    [r'FAIL(ED|\:)', r'\.\.\.\s(FAIL|ERROR)$'])
                context.o.auto_greens.extend([r'^OK$', r'\.\.\.\sok$'])
                context.o.auto_blues.extend([r'^Ran \d+ test'])
                context.o.default('\n')
                for line in stream.getvalue().splitlines(True):
                    context.o.auto(line, stream=PrettyOutput.stderr)

        return ok


class TestUnitTests(unittest.TestCase):
    def test_sanity(self):
        self.assertEqual(1, 1)
