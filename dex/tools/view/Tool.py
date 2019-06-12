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
"""View tool."""

import os

import pickle
from dex.heuristic import Heuristic
from dex.heuristic.Heuristic import add_heuristic_tool_arguments
from dex.tools import ToolBase
from dex.utils.Exceptions import Error, HeuristicException

class Tool(ToolBase):
    """Given a dextIR file, display the information in a human-readable form.
    """

    @property
    def name(self):
        return 'DExTer view'

    def add_tool_arguments(self, parser, defaults):
        add_heuristic_tool_arguments(parser)
        parser.add_argument(
            'input_path',
            metavar='dextIR-file',
            type=str,
            default=None,
            help='dexter dextIR file to view')
        parser.description = Tool.__doc__

    def handle_options(self, defaults):
        options = self.context.options

        options.input_path = os.path.abspath(options.input_path)
        if not os.path.isfile(options.input_path):
            raise Error('<d>could not find dextIR file</> <r>"{}"</>'.format(
                options.input_path))

    def go(self):
        options = self.context.options

        with open(options.input_path, 'rb') as fp:
            steps = pickle.load(fp)

        try:
            heuristic = Heuristic(self.context, steps)
        except HeuristicException as e:
            raise Error('could not apply heuristic: {}'.format(e))

        self.context.o.auto('{}\n\n{}\n\n{}\n\n'.format(
            heuristic.summary_string, steps, heuristic.verbose_output))

        return 0
