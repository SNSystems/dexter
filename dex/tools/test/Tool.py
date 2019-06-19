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
"""Test tool."""

import os
import csv

from dex.builder import run_external_build_script
from dex.debugger.Debuggers import get_debugger_steps
from dex.heuristic import Heuristic
from dex.tools import TestToolBase
from dex.utils.Exceptions import DebuggerException
from dex.utils.Exceptions import BuildScriptException, HeuristicException
from dex.utils.PrettyOutputBase import Stream


class TestCase(object):
    def __init__(self, context, name, heuristic, error):
        self.context = context
        self.name = name
        self.heuristic = heuristic
        self.error = error

    @property
    def penalty(self):
        try:
            return self.heuristic.penalty
        except AttributeError:
            return float('nan')

    @property
    def max_penalty(self):
        try:
            return self.heuristic.max_penalty
        except AttributeError:
            return float('nan')

    @property
    def score(self):
        try:
            return self.heuristic.score
        except AttributeError:
            return float('nan')

    def __str__(self):
        if self.error and self.context.options.verbose:
            verbose_error = str(self.error)
        else:
            verbose_error = ''

        if self.error:
            script_error = (' : {}'.format(
                self.error.script_error.splitlines()[0].decode()) if getattr(
                    self.error, 'script_error', None) else '')

            error = ' [{}{}]'.format(
                str(self.error).splitlines()[0], script_error)
        else:
            error = ''

        try:
            summary = self.heuristic.summary_string
        except AttributeError:
            summary = '<r>nan/nan (nan)</>'
        return '{}: {}{}\n{}'.format(self.name, summary, error, verbose_error)


class Tool(TestToolBase):
    """Run the specified DExTer test(s) with the specified compiler and linker
    options and produce dextIR output as a JSON file as well as printing out
    the debugging experience score calculated by the DExTer heuristic.
    """

    def __init__(self, *args, **kwargs):
        super(Tool, self).__init__(*args, **kwargs)
        self._test_cases = []

    @property
    def name(self):
        return 'DExTer test'

    def _run_test(self, subdir, test_name):
        options = self.context.options
        test_name = os.path.relpath(subdir, options.tests_directory)
        if os.path.split(test_name)[-1] == '.':
            test_name = os.path.basename(subdir)

        compiler_options = [options.cflags for _ in options.source_files]
        linker_options = options.ldflags
        try:
            _, _, builderIR = run_external_build_script(
                self.context,
                script_path=self.build_script,
                source_files=options.source_files,
                compiler_options=compiler_options,
                linker_options=linker_options,
                executable_file=options.executable)
        except BuildScriptException as e:
            test_case = TestCase(self.context, test_name, None, e)
            self.context.o.auto(test_case)
            self._test_cases.append(test_case)
            return

        try:
            steps = get_debugger_steps(self.context)
            steps.builder = builderIR
        except DebuggerException as e:
            test_case = TestCase(self.context, test_name, None, e)
            self.context.o.auto(test_case)
            self._test_cases.append(test_case)
            return

        test_results_path = os.path.join(options.results_directory, '_'.join(
            os.path.split(test_name)))
        output_text_path = '{}.txt'.format(test_results_path)
        with open(output_text_path, 'w') as fp:
            self.context.o.auto(str(steps), stream=Stream(fp))

        output_json_path = '{}.json'.format(test_results_path)
        with open(output_json_path, 'w') as fp:
            fp.write(steps.as_json)

        try:
            heuristic = Heuristic(self.context, steps)
        except HeuristicException as e:
            test_case = TestCase(self.context, test_name, None, e)
            self.context.o.auto(test_case)
            self._test_cases.append(test_case)
            return

        with open(output_text_path, 'a') as fp:
            self.context.o.auto(heuristic.verbose_output, stream=Stream(fp))

        test_case = TestCase(self.context, test_name, heuristic, None)
        self.context.o.auto(test_case)
        self._test_cases.append(test_case)

        if options.verbose:
            self.context.o.auto('\n{}\n'.format(steps))
            self.context.o.auto(heuristic.verbose_output)

    def _handle_results(self):
        options = self.context.options

        if not options.verbose:
            self.context.o.auto('\n')

        summary_path = os.path.join(options.results_directory, 'summary.csv')
        with open(summary_path, mode='w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',')
            writer.writerow(['Test Case', 'Score', 'Error'])

            for test_case in self._test_cases:
                writer.writerow([
                    test_case.name, '{:.4f}'.format(test_case.score),
                    test_case.error
                ])

        return 0
