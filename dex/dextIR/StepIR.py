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
"""Classes which are used to represent debugger steps."""

import json

from collections import OrderedDict
from typing import List
from enum import Enum
from dex.dextIR.FrameIR import FrameIR
from dex.dextIR.LocIR import LocIR
from dex.dextIR.ProgramState import ProgramState


class StopReason(Enum):
    BREAKPOINT = 0
    STEP = 1
    PROGRAM_EXIT = 2
    ERROR = 3
    OTHER = 4


class StepKind(Enum):
    FUNC = 0
    FUNC_EXTERNAL = 1
    FUNC_UNKNOWN = 2
    FORWARD = 3
    SAME = 4
    BACKWARD = 5
    UNKNOWN = 6


class StepIR:
    """A debugger step.

    Args:
        watches (OrderedDict): { expression (str), result (ValueIR) }
    """

    def __init__(self,
                 step_index: int,
                 stop_reason: StopReason,
                 frames: List[FrameIR],
                 step_kind: StepKind = None,
                 watches: OrderedDict = None,
                 program_state: ProgramState = None):
        self.step_index = step_index
        self.step_kind = step_kind
        self.stop_reason = stop_reason
        self.program_state = program_state

        if frames is None:
            frames = []
        self.frames = frames

        if watches is None:
            watches = {}
        self.watches = watches

    def __str__(self):
        try:
            frame = self.current_frame
            frame_info = (frame.function, frame.loc.path, frame.loc.lineno,
                          frame.loc.column)
        except AttributeError:
            frame_info = (None, None, None, None)

        step_info = (self.step_index, ) + frame_info + (
            str(self.stop_reason), str(self.step_kind),
                                    [w for w in self.watches])

        return '{}{}'.format('.   ' * (self.num_frames - 1),
                             json.dumps(step_info))

    @property
    def num_frames(self):
        return len(self.frames)

    @property
    def current_frame(self):
        if not len(self.frames):
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
            return self.current_frame.loc
        except AttributeError:
            return LocIR(path=None, lineno=None, column=None)
