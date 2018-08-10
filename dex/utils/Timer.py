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
"""RAII-style timer class to be used with a 'with' statement to get wall clock
time for the contained code.
"""

import sys
import time


def _indent(indent):
    return '| ' * indent


class Timer(object):
    fn = sys.stdout.write
    display = False
    indent = 0

    def __init__(self, name=None):
        self.name = name
        self.start = self.now

    def __enter__(self):
        Timer.indent += 1
        if Timer.display and self.name:
            indent = _indent(Timer.indent - 1) + ' _'
            Timer.fn('{}\n'.format(_indent(Timer.indent - 1)))
            Timer.fn('{} start {}\n'.format(indent, self.name))
        return self

    def __exit__(self, *args):
        if Timer.display and self.name:
            indent = _indent(Timer.indent - 1) + '|_'
            Timer.fn('{} {} time taken: {:0.1f}s\n'.format(
                indent, self.name, self.elapsed))
            Timer.fn('{}\n'.format(_indent(Timer.indent - 1)))
        Timer.indent -= 1

    @property
    def elapsed(self):
        return self.now - self.start

    @property
    def now(self):
        return time.time()
