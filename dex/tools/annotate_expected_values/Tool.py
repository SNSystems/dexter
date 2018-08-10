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
"""Annotate Expected Values Tool."""

import os

from dex.dextIR.DextIR import importDextIR
from dex.dextIR.StepIR import StepKind
from dex.tools import ToolBase
from dex.utils.Exceptions import Error, ImportDextIRException


class ExpectedWatchValue(object):
    def __init__(self, file_path, expression, start_value, line_seen):
        self.file_path = file_path
        self.expression = expression
        self.values = [start_value]
        self.last_line_seen = line_seen
        self.from_line = line_seen
        self.to_line = line_seen
        self.last_value_seen = start_value

    def __eq__(self, other):
        return (self.file_path == other.file_path
                and self.expression == other.expression
                and self.from_line == other.from_line
                and self.to_line == other.to_line)

    def __hash__(self):
        return hash((self.file_path, self.expression, self.from_line,
                     self.to_line))

    def add_value(self, value, line_seen):
        if line_seen < self.from_line:
            self.from_line = line_seen
        if line_seen > self.to_line:
            self.to_line = line_seen

        if self.last_value_seen == value:
            return

        self.values.append(value)
        self.last_value_seen = value
        self.last_line_seen = line_seen

    def is_out_of_range(self, lineno):
        return ((lineno < self.from_line - 1 or lineno > self.to_line + 1)
                and abs(lineno - self.last_line_seen) > 2)

    def __str__(self):
        if self.from_line == self.to_line:
            from_to = 'on_line={}'.format(self.from_line)
        else:
            from_to = 'from_line={}, to_line={}'.format(
                self.from_line, self.to_line)

        return ("// DexExpectWatchValue('{}', {}, {})".format(
            self.expression, ', '.join(str(v) for v in self.values), from_to))


class ExpectedStepKind(object):
    def __init__(self, name, start_count):
        self.name = name
        self.count = start_count

    def increase_count(self):
        self.count += 1


class Tool(ToolBase):
    """Given a JSON dextIR file, attempt to automatically provide automatic
    DExTer command annotations based on that output.  Typically, this would be
    from an unoptimized build.

    It is expected that these automatically generated annotations will need
    some manual fix-ups to become generic enough to be useful, but it is hoped
    that this tool will provide a starting point to speed up the overall
    process.
    """

    @property
    def name(self):
        return 'DExTer annotate expected values'

    def add_tool_arguments(self, parser, defaults):
        parser.description = Tool.__doc__
        parser.add_argument(
            'json_file',
            metavar='dexter-json-file',
            type=str,
            help='dexter json file to read')
        parser.add_argument(
            'source_files',
            metavar='source-file',
            type=str,
            nargs='+',
            help='source files to annotate')

    def handle_options(self, defaults):
        options = self.context.options

        options.json_file = os.path.abspath(options.json_file)
        if not os.path.isfile(options.json_file):
            raise Error('<d>could not find</> <r>"{}"</>'.format(
                options.json_file))

        options.source_files = [
            os.path.normcase(os.path.abspath(sf))
            for sf in options.source_files
        ]
        for sf in options.source_files:
            if not os.path.isfile(sf):
                if os.path.exists(sf):
                    raise Error('"{}" <d>is not a valid file</>'.format(sf))
                raise Error('<d>could not find file</> "{}"'.format(sf))

    def go(self):  # noqa
        options = self.context.options

        exp_values = set()
        step_kinds = []

        for step_kind in StepKind.possible_values:
            step_kinds.append(ExpectedStepKind(step_kind, 0))

        with open(options.json_file) as fp:
            try:
                step_collection = importDextIR(fp.read())
            except ImportDextIRException as e:
                raise Error(
                    '<d>could not import</> <r>"{}"</>: <d>{}</>'.format(
                        options.json_file, e))

        for step in getattr(step_collection, 'steps'):
            lineno = step.current_location.lineno

            for step_kind in step_kinds:
                if step_kind.name == step.step_kind:
                    step_kind.increase_count()

            for value_info in step.watches.values():
                if value_info.value is None:
                    continue

                found_exp_val = False
                is_pointer = value_info.value.startswith('0x')

                for exp_value in exp_values:
                    if exp_value.expression == value_info.expression:
                        if exp_value.is_out_of_range(lineno):
                            exp_values.add(
                                ExpectedWatchValue(
                                    step.current_location.path,
                                    value_info.expression, "'{}'".format(
                                        value_info.value), lineno))
                            found_exp_val = True
                            break

                        if not is_pointer:
                            exp_value.add_value(
                                "'{}'".format(value_info.value), lineno)

                        found_exp_val = True
                        break

                if not found_exp_val:
                    exp_values.add(
                        ExpectedWatchValue(
                            step.current_location.path, value_info.expression,
                            "'{}'".format(value_info.value), lineno))

        for source_file in options.source_files:
            with open(source_file, 'a') as fp:
                exp_values_trimmed = [
                    v for v in exp_values if v.file_path == source_file
                ]

                if exp_values_trimmed:
                    fp.write('\n\n')

                    prev_from_line = -1
                    for exp_value in sorted(
                            exp_values_trimmed,
                            key=lambda v: (v.from_line, v.expression)):
                        if exp_value.from_line != prev_from_line:
                            fp.write('\n')
                            prev_from_line = exp_value.from_line
                        fp.write('\n{}'.format(exp_value))

        with open(options.source_files[0], 'a') as fp:
            if step_kinds:
                fp.write('\n\n')

                for step_kind in step_kinds:
                    fp.write("\n// DexExpectStepKind('{}', {})".format(
                        step_kind.name, step_kind.count))

        return 0
