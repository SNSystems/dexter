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
"""Set of data classes for representing the complete debug program state at a
fixed point in execution.
"""

import os

from collections import OrderedDict
from typing import List

class SourceLocation:
    def __init__(self, path: str = None, lineno: int = None, column: int = None):
        if path:
            path = os.path.normcase(path)
        self.path = path
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return '{}({}:{})'.format(self.path, self.lineno, self.column)

    def match(self, other) -> bool:
        """Returns true iff all the properties that appear in `self` have the
        same value in `other`, but not necessarily vice versa.
        """
        if not other or not isinstance(other, SourceLocation):
            return False

        if self.path and (self.path != other.path):
            return False

        if self.lineno and (self.lineno != other.lineno):
            return False

        if self.column and (self.column != other.column):
            return False

        return True


class StackFrame:
    def __init__(self,
                 function: str = None,
                 is_inlined: bool = None,
                 location: SourceLocation = None,
                 watches: OrderedDict = None):
        if watches is None:
            watches = {}

        self.function = function
        self.is_inlined = is_inlined
        self.location = location
        self.watches = watches

    def __str__(self):
        return '{}{}: {} | {}'.format(
            self.function,
            ' (inlined)' if self.is_inlined else '',
            self.location,
            {k: str(self.watches[k]) for k in self.watches})

    def match(self, other) -> bool:
        """Returns true iff all the properties that appear in `self` have the
        same value in `other`, but not necessarily vice versa.
        """
        if not other or not isinstance(other, StackFrame):
            return False

        if self.location and not self.location.match(other.location):
            return False

        if self.watches:
            for name in iter(self.watches):
                try:
                    for attr in iter(self.watches[name]):
                        if (getattr(other.watches[name], attr, None) !=
                                self.watches[name][attr]):
                            return False
                except KeyError:
                    return False

        return True

class ProgramState:
    def __init__(self, frames: List[StackFrame] = None):
        self.frames = frames

    def __str__(self):
        return '\n'.join(map(
            lambda enum: 'Frame {}: {}'.format(enum[0], enum[1]),
            enumerate(self.frames)))

    def match(self, other) -> bool:
        """Returns true iff all the properties that appear in `self` have the
        same value in `other`, but not necessarily vice versa.
        """
        if not other or not isinstance(other, ProgramState):
            return False

        if self.frames:
            for idx, frame in enumerate(self.frames):
                try:
                    if not frame.match(other.frames[idx]):
                        return False
                except (IndexError, KeyError):
                    return False

        return True
