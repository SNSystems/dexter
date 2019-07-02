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
import pickle

from dex.builder import run_external_build_script
from dex.debugger.Debuggers import get_debugger_steps
from dex.heuristic import Heuristic
from dex.tools import TestToolBase
from dex.utils.Exceptions import DebuggerException
from dex.utils.Exceptions import BuildScriptException, HeuristicException
from dex.utils.PrettyOutputBase import Stream
from dex.utils.ReturnCode import ReturnCode


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
    options and produce a dextIR file as well as printing out the debugging
    experience score calculated by the DExTer heuristic.
    """

    def __init__(self, *args, **kwargs):
        super(Tool, self).__init__(*args, **kwargs)
        self._test_cases = []

    @property
    def name(self):
        return 'DExTer test'

    def add_tool_arguments(self, parser, defaults):
        parser.add_argument('--fail-lt',
                            type=float,
                            default=0.0, # By default TEST always succeeds.
                            help='exit with status FAIL(2) if the test result'
                                ' is less than this value.',
                            metavar='<float>')
        super(Tool, self).add_tool_arguments(parser, defaults)

    def _build_test_case(self):
        """Invoke the specified builder script to build the test case
           with the specified cflags and ldflags.
        """
        options = self.context.options
        compiler_options = [options.cflags for _ in options.source_files]
        linker_options = options.ldflags
        _, _, builderIR = run_external_build_script(
            self.context,
            script_path=self.build_script,
            source_files=options.source_files,
            compiler_options=compiler_options,
            linker_options=linker_options,
            executable_file=options.executable)
        return builderIR

    def _get_steps(self, builderIR):
        """Generate a list of debugger steps from a test case.
        """
        steps = get_debugger_steps(self.context)
        steps.builder = builderIR
        return steps

    def _get_results_path(self, test_name):
        """Returns the path to the test results directory for the test denoted
           by test_name.
        """
        return os.path.join(self.context.options.results_directory, '_'.join(
            os.path.split(test_name)))

    def _get_results_text_path(self, test_name):
        """Returns path results .txt file for test denoted by test_name.
        """
        test_results_path = self._get_results_path(test_name)
        return '{}.txt'.format(test_results_path)

    def _get_results_json_path(self, test_name):
        """Returns path to results .json file for test denoted by test_name.
        """
        test_results_path = self._get_results_path(test_name)
        return '{}.json'.format(test_results_path)

    def _record_steps(self, test_name, steps):
        """Write out the set of steps out to the test's .txt and .json
           results file.
        """
        output_text_path = self._get_results_text_path(test_name)
        with open(output_text_path, 'w') as fp:
            self.context.o.auto(str(steps), stream=Stream(fp))

        output_dextIR_path = '{}.dextIR'.format(test_name)
        with open(output_dextIR_path, 'wb') as fp:
            pickle.dump(steps, fp)

    def _record_score(self, test_name, heuristic):
        """Write out the test's heuristic score to the results .txt file.
        """
        output_text_path = self._get_results_text_path(test_name)
        with open(output_text_path, 'a') as fp:
            self.context.o.auto(heuristic.verbose_output, stream=Stream(fp))

    def _record_test_and_display(self, test_case):
        """Output test case to o stream and record test case internally for
           handling later.
        """
        self.context.o.auto(test_case)
        self._test_cases.append(test_case)

    def _record_failed_test(self, test_name, exception):
        """Instantiate a failed test case with failure exception and
           store internally.
        """
        test_case = TestCase(self.context, test_name, None, exception)
        self._record_test_and_display(test_case)

    def _record_successful_test(self, test_name, steps, heuristic):
        """Instantiate a successful test run, store test for handling later.
           Display verbose output for test case if required.
        """
        test_case = TestCase(self.context, test_name, heuristic, None)
        self._record_test_and_display(test_case)
        if self.context.options.verbose:
            self.context.o.auto('\n{}\n'.format(steps))
            self.context.o.auto(heuristic.verbose_output)

    def _run_test(self, test_dir):
        """Attempt to run test case found in test_dir. Store result internally
           in self._test_cases.
        """
        test_name = self._get_test_name(test_dir)
        try:
            builderIR = self._build_test_case()
            steps = self._get_steps(builderIR)
            self._record_steps(test_name, steps)
            heuristic_score = Heuristic(self.context, steps)
            self._record_score(test_name, heuristic_score)
        except (BuildScriptException, DebuggerException,
                HeuristicException) as e:
            self._record_failed_test(test_name, e)
            return

        self._record_successful_test(test_name, steps, heuristic_score)
        return

    def _handle_results(self) -> ReturnCode:
        return_code = ReturnCode.OK
        options = self.context.options

        if not options.verbose:
            self.context.o.auto('\n')

        summary_path = os.path.join(options.results_directory, 'summary.csv')
        with open(summary_path, mode='w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',')
            writer.writerow(['Test Case', 'Score', 'Error'])

            for test_case in self._test_cases:
                if test_case.score < options.fail_lt:
                    return_code = ReturnCode.FAIL

                writer.writerow([
                    test_case.name, '{:.4f}'.format(test_case.score),
                    test_case.error
                ])

        return return_code
