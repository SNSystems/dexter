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
                 local_vars: OrderedDict = None):
        if local_vars is None:
            local_vars = {}

        self.function = function
        self.is_inlined = is_inlined
        self.location = location
        self.local_vars = local_vars

    def __str__(self):
        return '{}{}: {} | {}'.format(
            self.function,
            ' (inlined)' if self.is_inlined else '',
            self.location,
            self.local_vars)

    def match(self, other) -> bool:
        if not other or not isinstance(other, StackFrame):
            return False

        if self.location and not self.location.match(other.location):
            return False

        if self.local_vars:
            for name in iter(self.local_vars):
                try:
                    if other.local_vars[name] != self.local_vars[name]:
                        return False
                except KeyError:
                    return False

        return True

class ProgramState:
    def __init__(self,
                 frames: List[StackFrame] = None,
                 global_vars: OrderedDict = None):
        self.frames = frames
        self.global_vars = global_vars

    def __str__(self):
        return '\n'.join(map(
            lambda enum: 'Frame {}: {}'.format(enum[0], enum[1]),
            enumerate(self.frames)))

    def match(self, other) -> bool:
        if not other or not isinstance(other, ProgramState):
            return False

        if self.frames:
            for idx, frame in enumerate(self.frames):
                try:
                    if not frame.match(other.frames[idx]):
                        return False
                except (IndexError, KeyError):
                    return False

        if self.global_vars:
            for name in iter(self.global_vars):
                try:
                    if other.global_variables[name] != self.global_vars[name]:
                        return False
                except IndexError:
                    return False

        return True
