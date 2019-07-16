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
from collections import OrderedDict
from typing import List

from dex.dextIR.BuilderIR import BuilderIR
from dex.dextIR.DebuggerIR import DebuggerIR
from dex.dextIR.StepIR import StepIR, StepKind


def _step_kind_func(context, step):
    if step.current_location.path in context.options.source_files:
        return StepKind.FUNC

    if step.current_location.path is None:
        return StepKind.FUNC_UNKNOWN

    return StepKind.FUNC_EXTERNAL


class DextIR:
    """A full Dexter test report.

    This is composed of all the other *IR classes. They are used together to
    record Dexter inputs and the resultant debugger steps, providing a single
    high level access container.

    The Heuristic class works with dexter commands and the generated DextIR to
    determine the debugging score for a given test.

    Args:
        commands: { name (str), commands (list[CommandIR])
    """

    def __init__(self,
                 dexter_version: str,
                 executable_path: str,
                 source_paths: List[str],
                 builder: BuilderIR = None,
                 debugger: DebuggerIR = None,
                 commands: OrderedDict = None):
        self.dexter_version = dexter_version
        self.executable_path = executable_path
        self.source_paths = source_paths
        self.builder = builder
        self.debugger = debugger
        self.commands = commands
        self.steps: List[StepIR] = []

    def __str__(self):
        colors = 'rgby'
        st = '## BEGIN ##\n'
        color_idx = 0
        for step in self.steps:
            if step.step_kind in (StepKind.FUNC, StepKind.FUNC_EXTERNAL,
                                  StepKind.FUNC_UNKNOWN):
                color_idx += 1

            color = colors[color_idx % len(colors)]
            st += '<{}>{}</>\n'.format(color, step)
        st += '## END ({} step{}) ##\n'.format(
            self.num_steps, '' if self.num_steps == 1 else 's')
        return st

    @property
    def num_steps(self):
        return len(self.steps)

    def new_step(self, context, step):
        assert isinstance(step, StepIR), type(step)
        if step.current_function is None:
            step.step_kind = StepKind.UNKNOWN
        else:
            try:
                prev_step = self.steps[-1]
            except IndexError:
                step.step_kind = _step_kind_func(context, step)
            else:
                if prev_step.current_function is None:
                    step.step_kind = StepKind.UNKNOWN
                elif prev_step.current_function != step.current_function:
                    step.step_kind = _step_kind_func(context, step)
                elif prev_step.current_location == step.current_location:
                    step.step_kind = StepKind.SAME
                elif prev_step.current_location > step.current_location:
                    step.step_kind = StepKind.BACKWARD
                elif prev_step.current_location < step.current_location:
                    step.step_kind = StepKind.FORWARD

        self.steps.append(step)
        return step

    def clear_steps(self):
        self.steps.clear()
