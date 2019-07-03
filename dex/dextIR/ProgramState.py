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

    def match(self, other) -> bool:
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

    def match(self, other) -> bool:
        if self.location and not self.location.match(other.source_loc):
            return False

        if self.local_vars:
            for key, val in enumerate(self.local_vars):
                try:
                    if other.local_variables[key] != val:
                        return False
                except IndexError:
                    return False

        return True

class ProgramState:
    def __init__(self,
                 frames: List[StackFrame] = None,
                 global_vars: OrderedDict = None):
        if frames is None:
            frames = []
        self.frames = frames

        if global_vars is None:
            global_vars = {}
        self.global_vars = global_vars

    @property
    def num_frames(self):
        return len(self.frames)

    @property
    def current_frame(self):
        if not self.frames:
            return None
        return self.frames[0]

    @property
    def current_function(self):
        try:
            return self.current_frame.function
        except AttributeError:
            return None

    @property
    def current_location(self):
        try:
            return self.current_frame.source_loc
        except AttributeError:
            return SourceLocation(path=None, lineno=None, column=None)

    def match(self, other) -> bool:
        if self.frames:
            for idx, frame in enumerate(self.frames):
                try:
                    if not frame.match(other.frames[idx]):
                        return False
                except IndexError:
                    return False

        if self.global_vars:
            for key, val in enumerate(self.global_vars):
                try:
                    if other.global_variables[key] != val:
                        return False
                except IndexError:
                    return False

        return True
