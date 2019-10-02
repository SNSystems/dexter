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

import sys
import os

from dex.debugger.DebuggerBase import DebuggerBase
from dex.dextIR import FrameIR, LocIR, StepIR, StopReason, ValueIR
from dex.dextIR import ProgramState, StackFrame, SourceLocation
from dex.utils.Exceptions import DebuggerException, LoadDebuggerException
from dex.utils.ReturnCode import ReturnCode

from . import setup
from . import probe_process
from . import breakpoint

class DbgEng(DebuggerBase):
    def __init__(self, context, *args):
        self.breakpoints = []
        self.running = False
        self.finished = False
        self.step_info = None
        super(DbgEng, self).__init__(context, *args)

    def _custom_init(self):
        try:
          res = setup.setup_everything(self.context.options.executable)
          self.client, self.hProcess = res
          self.running = True
        except Exception as e:
          raise Exception('Failed to start debuggee: {}'.format(e))

    def _custom_exit(self):
        setup.cleanup(self.client, self.hProcess)

    def _load_interface(self):
        pass

    @classmethod
    def get_name(cls):
        return 'dbgeng'

    @classmethod
    def get_option_name(cls):
        return 'dbgeng'

    @property
    def frames_below_main(self):
        return []

    @property
    def version(self):
        # I don't believe there's a well defined DbgEng version, outside of the
        # version of Windows being used.
        return "1"

    def clear_breakpoints(self):
        for x in self.breakpoints:
            x.RemoveFlags(breakpoint.BreakpointFlags.DEBUG_BREAKPOINT_ENABLED)
            self.client.Control.RemoveBreakpoint(x)

    def add_breakpoint(self, file_, line):
        # This is something to implement in the future -- as it stands, Dexter
        # doesn't test for such things as "I can set a breakpoint on this line".
        # This is only called AFAICT right now to ensure we break on every step.
        pass

    def launch(self):
        # We are, by this point, already launched.
        self.step_info = probe_process.probe_state(self.client)

    def step(self):
        res = setup.step_once(self.client)
        if not res:
          self.finished = True
        self.step_info = res

    def go(self):
        # We never go -- we always single step.
        pass

    def get_step_info(self):
        frames = self.step_info
        state_frames = []

        # For now assume the base function is the... function, ignoring
        # inlining.
        dex_frames = []
        for i, x in enumerate(frames):
          # XXX Might be able to get columns out through
          # GetSourceEntriesByOffset, not a priority now
          loc = LocIR(path=x.source_file, lineno=x.line_no, column=0)
          new_frame = FrameIR(function=x.function_name, is_inlined=False, loc=loc)
          dex_frames.append(new_frame)

          state_frame = StackFrame(function=new_frame.function,
                                   is_inlined=new_frame.is_inlined,
                                   location=SourceLocation(path=x.source_file,
                                                           lineno=x.line_no,
                                                           column=0),
                                   watches={})
          for expr in map(
              lambda watch, idx=i: self.evaluate_expression(watch, idx),
              self.watches):
              state_frame.watches[expr.expression] = expr
          state_frames.append(state_frame)

        return StepIR(
            step_index=self.step_index, frames=dex_frames,
            stop_reason=StopReason.STEP,
            program_state=ProgramState(state_frames))

    @property
    def is_running(self):
        return False # We're never free-running

    @property
    def is_finished(self):
        return self.finished

    def evaluate_expression(self, expression, frame_idx=0):
        # TODO: evaluate expressions in the right stack frame?
        res = self.client.Control.Evaluate(expression)
        if res is not None:
          result, typename = self.client.Control.Evaluate(expression)
          could_eval = True
        else:
          result, typename = (None, None)
          could_eval = False

        return ValueIR(
            expression=expression,
            value=str(result),
            type_name=typename,
            error_string="",
            could_evaluate=could_eval,
            is_optimized_away=False,
            is_irretrievable=False)
