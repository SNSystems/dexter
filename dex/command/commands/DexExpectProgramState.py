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
"""Command for specifying a partial or complete state for the program to enter
during execution.
"""

from dex.command.CommandBase import CommandBase
from dex.dextIR import ProgramState, SourceLocation, StackFrame, DextIR

def frame_from_dict(source: dict) -> StackFrame:
    if 'location' in source:
        assert isinstance(source['location'], dict)
        source['location'] = SourceLocation(**source['location'])
    return StackFrame(**source)

def state_from_dict(source: dict) -> ProgramState:
    if 'frames' in source:
        assert isinstance(source['frames'], list)
        source['frames'] = list(map(frame_from_dict, source['frames']))
    return ProgramState(**source)

class DexExpectProgramState(CommandBase):
    def __init__(self, *args, **kwargs):
        if len(args) != 1:
            raise TypeError('expected exactly one unnamed arg')

        self.program_state_text = str(args[0])

        self.expected_program_state = state_from_dict(args[0])

        self.times = kwargs.pop('times', -1)
        if kwargs:
            raise TypeError('unexpected named args: {}'.format(
                ', '.join(kwargs)))

        # Step indices at which the expected program state was encountered.
        self.encounters = []

        super(DexExpectProgramState, self).__init__()

    @staticmethod
    def get_name():
        return __class__.__name__

    def eval(self, step_collection: DextIR) -> bool:
        for step in step_collection.steps:
            if self.expected_program_state.match(step.program_state):
                self.encounters.append(step.step_index)

        return self.times < 0 < len(self.encounters) or len(self.encounters) == self.times
