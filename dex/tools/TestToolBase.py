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
"""Base class for subtools that do build/run tests."""

import abc
from datetime import datetime
import os

from dex.builder import add_builder_tool_arguments
from dex.builder import handle_builder_tool_options
from dex.debugger.Debuggers import add_debugger_tool_arguments
from dex.debugger.Debuggers import handle_debugger_tool_options
from dex.heuristic.Heuristic import add_heuristic_tool_arguments
from dex.tools.ToolBase import ToolBase
from dex.utils import get_root_directory
from dex.utils.Exceptions import Error, ToolArgumentError


class TestToolBase(ToolBase):
    def add_tool_arguments(self, parser, defaults):
        parser.description = self.__doc__
        add_builder_tool_arguments(parser)
        add_debugger_tool_arguments(parser, self.context, defaults)
        add_heuristic_tool_arguments(parser)

        parser.add_argument(
            'tests_directory',
            type=str,
            metavar='<tests-directory>',
            nargs='?',
            default=os.path.abspath(
                os.path.join(get_root_directory(), '..', 'tests')),
            help='directory containing test(s)')

        parser.add_argument(
            '--results-directory',
            type=str,
            metavar='<directory>',
            default=os.path.abspath(
                os.path.join(get_root_directory(), '..', 'results',
                             datetime.now().strftime('%Y-%m-%d-%H%M-%S'))),
            help='directory to save results')

    def handle_options(self, defaults):
        try:
            handle_builder_tool_options(self.context)
        except ToolArgumentError as e:
            raise Error(e)

        try:
            handle_debugger_tool_options(self.context, defaults)
        except ToolArgumentError as e:
            raise Error(e)

        options = self.context.options

        options.tests_directory = os.path.abspath(options.tests_directory)
        if not os.path.isdir(options.tests_directory):
            raise Error(
                '<d>could not find tests directory</> <r>"{}"</>'.format(
                    options.tests_directory))

        options.results_directory = os.path.abspath(options.results_directory)
        if not os.path.isdir(options.results_directory):
            try:
                os.makedirs(options.results_directory)
            except OSError as e:
                raise Error(
                    '<d>could not create directory</> <r>"{}"</> <y>({})</>'.
                    format(options.results_directory, e.strerror))

    def go(self):  # noqa
        options = self.context.options

        subdirs = sorted([
            r for r, _, f in os.walk(options.tests_directory)
            if 'test.cfg' in f
        ])

        for subdir in subdirs:
            test_name = os.path.basename(subdir)

            # TODO: read file extensions from the test.cfg file instead so that
            # this isn't just limited to C and C++.
            options.source_files = [
                os.path.normcase(os.path.join(subdir, f))
                for f in os.listdir(subdir) if any(
                    f.endswith(ext) for ext in ['.c', '.cpp'])
            ]

            options.executable = os.path.join(
                self.context.working_directory.path, 'tmp.exe')

            self._run_test(subdir, test_name)

        self._handle_results()

    @abc.abstractmethod
    def _run_test(self, subdir, test_name):
        pass

    @abc.abstractmethod
    def _handle_results(self):
        pass
