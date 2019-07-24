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
import os


class LocIR:
    """Data class which represents a source location."""

    def __init__(self, path: str, lineno: int, column: int):
        if path:
            path = os.path.normcase(path)
        self.path = path
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return '{}({}:{})'.format(self.path, self.lineno, self.column)

    def __eq__(self, rhs):
        return (self.path == rhs.path and self.lineno == rhs.lineno
                and self.column == rhs.column)

    def __lt__(self, rhs):
        if self.path != rhs.path:
            return False

        if self.lineno == rhs.lineno:
            return self.column < rhs.column

        return self.lineno < rhs.lineno

    def __gt__(self, rhs):
        if self.path != rhs.path:
            return False

        if self.lineno == rhs.lineno:
            return self.column > rhs.column

        return self.lineno > rhs.lineno
