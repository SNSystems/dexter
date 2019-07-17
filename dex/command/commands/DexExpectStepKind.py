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
"""Command for specifying an expected number of steps of a particular kind."""

from dex.command.CommandBase import CommandBase
from dex.dextIR.StepIR import StepKind


class DexExpectStepKind(CommandBase):
    def __init__(self, *args):
        if len(args) != 2:
            raise TypeError('expected two args')

        try:
            step_kind = StepKind[args[0]]
        except KeyError:
            raise TypeError('expected arg 0 to be one of {}'.format(
                [kind for kind, _ in StepKind.__members__.items()]))

        self.name = step_kind
        self.count = args[1]

        super(DexExpectStepKind, self).__init__()

    @staticmethod
    def get_name():
        return __class__.__name__

    def eval(self):
        pass
