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
"""Serialization of information related to a debugger step."""

from collections import OrderedDict
import json

from dex.dextIR.FrameIR import FrameIR
from dex.dextIR.LocIR import LocIR
from dex.dextIR.ValueIR import ValueIR
from dex.utils import create_named_enum
from dex.utils.compatibility import string_types
from dex.utils.serialize import SrField, SrObject

StopReason = create_named_enum('BREAKPOINT', 'STEP', 'PROGRAM_EXIT', 'ERROR',
                               'OTHER')

StepKind = create_named_enum('FUNC', 'FUNC_EXTERNAL', 'FUNC_UNKNOWN',
                             'FORWARD', 'SAME', 'BACKWARD', 'UNKNOWN')


# pylint: disable=no-member
class StepIR(SrObject):

    sr_fields = [
        SrField('step_index', int),
        SrField(
            'step_kind',
            string_types,
            required_in_init=False,
            default_value=StepKind.UNKNOWN,
            can_be_none=True,
            possible_values=StepKind.possible_values),
        SrField(
            'stop_reason',
            string_types,
            possible_values=StopReason.possible_values,
            can_be_none=True),
        SrField('frames', FrameIR, list_of=True),
        SrField(
            'watches',
            ValueIR,
            dict_of=True,
            required_in_init=False,
            default_value=OrderedDict),
    ]

    def __str__(self):
        try:
            frame = self.current_frame
            frame_info = (frame.function, frame.loc.path, frame.loc.lineno,
                          frame.loc.column)
        except AttributeError:
            frame_info = (None, None, None, None)

        watches = OrderedDict((w, self.watches[w].value) for w in self.watches)

        step_info = (self.step_index, ) + frame_info + (
            self.stop_reason, self.step_kind, watches)

        return '{}{}'.format('.   ' * (self.num_frames - 1),
                             json.dumps(step_info))

    @property
    def num_frames(self):
        return len(self.frames)

    @property
    def current_frame(self):
        try:
            return self.frames[0]
        except IndexError:
            return None

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
