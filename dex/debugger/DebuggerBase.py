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
"""Base class for all debugger interface implementations."""

import abc
from itertools import chain
import sys
import time
import traceback

from dex.dextIR import DebuggerIR
from dex.utils.Exceptions import DebuggerException
from dex.utils.Exceptions import NotYetLoadedDebuggerException
from dex.utils.ReturnCode import ReturnCode


class DebuggerBase(object, metaclass=abc.ABCMeta):
    def __init__(self, context, step_collection):
        self.context = context
        self.steps = step_collection
        self._interface = None
        self.has_loaded = False
        self._loading_error = NotYetLoadedDebuggerException()

        try:
            self._interface = self._load_interface()
            self.has_loaded = True
            self._loading_error = None
        except DebuggerException:
            self._loading_error = sys.exc_info()

        self.step_index = 0

    def __enter__(self):
        try:
            self._custom_init()
            self.clear_breakpoints()
            self.add_breakpoints()
        except DebuggerException:
            self._loading_error = sys.exc_info()
        return self

    def __exit__(self, *args):
        self._custom_exit()

    def _custom_init(self):
        pass

    def _custom_exit(self):
        pass

    @property
    def debugger_info(self):
        return DebuggerIR(name=self.name, version=self.version)

    @property
    def is_available(self):
        return self.has_loaded and self.loading_error is None

    @property
    def loading_error(self):
        return (str(self._loading_error[1])
                if self._loading_error is not None else None)

    @property
    def loading_error_trace(self):
        if not self._loading_error:
            return None

        tb = traceback.format_exception(*self._loading_error)

        if self._loading_error[1].orig_exception is not None:
            orig_exception = traceback.format_exception(
                *self._loading_error[1].orig_exception)

            if ''.join(orig_exception) not in ''.join(tb):
                tb.extend(['\n'])
                tb.extend(orig_exception)

        tb = ''.join(tb).splitlines(True)
        return tb

    def add_breakpoints(self):
        for s in self.context.options.source_files:
            with open(s, 'r') as fp:
                num_lines = len(fp.readlines())
            for line in range(1, num_lines + 1):
                self.add_breakpoint(s, line)

    def _update_step_watches(self, step_info):
        loc = step_info.current_location
        watch_cmds = ['DexWatch', 'DexUnreachable', 'DexExpectStepOrder']
        towatch = chain.from_iterable(self.steps.commands[x]
                                      for x in watch_cmds
                                      if x in self.steps.commands)
        try:
            # Iterate over all watches of the types named in watch_cmds
            for watch in towatch:
                if (watch.path == loc.path
                        and watch.lineno == loc.lineno):
                    result = watch.eval(self)
                    step_info.watches.update(result)
                    break
        except KeyError:
            pass

    def _sanitize_function_name(self, name):  # pylint: disable=no-self-use
        """If the function name returned by the debugger needs any post-
        processing to make it fit (for example, if it includes a byte offset),
        do that here.
        """
        return name

    def start(self):
        self.steps.clear_steps()
        self.launch()

        max_steps = self.context.options.max_steps
        for _ in range(max_steps):
            while self.is_running:
                pass

            if self.is_finished:
                break

            self.step_index += 1
            step_info = self.get_step_info()

            if step_info.current_frame:
                self._update_step_watches(step_info)
                self.steps.new_step(self.context, step_info)

            if (step_info.current_frame
                    and (step_info.current_location.path in
                         self.context.options.source_files)):
                self.step()
            else:
                self.go()

            time.sleep(self.context.options.pause_between_steps)
        else:
            raise DebuggerException(
                'maximum number of steps reached ({})'.format(max_steps))
    @abc.abstractmethod
    def _load_interface(self):
        pass

    @classmethod
    def get_option_name(cls):
        """Short name that will be used on the command line to specify this
        debugger.
        """
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        """Full name of this debugger."""
        raise NotImplementedError()

    @property
    def name(self):
        return self.__class__.get_name()

    @property
    def option_name(self):
        return self.__class__.get_option_name()

    @abc.abstractproperty
    def version(self):
        pass

    @abc.abstractmethod
    def clear_breakpoints(self):
        pass

    @abc.abstractmethod
    def add_breakpoint(self, file_, line):
        pass

    @abc.abstractmethod
    def launch(self):
        pass

    @abc.abstractmethod
    def step(self):
        pass

    @abc.abstractmethod
    def go(self) -> ReturnCode:
        pass

    @abc.abstractmethod
    def get_step_info(self):
        pass

    @abc.abstractproperty
    def is_running(self):
        pass

    @abc.abstractproperty
    def is_finished(self):
        pass

    @abc.abstractproperty
    def frames_below_main(self):
        pass

    @abc.abstractmethod
    def evaluate_expression(self, expression):
        pass
