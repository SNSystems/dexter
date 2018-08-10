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
"""This is a special subtool that is run when no subtool is specified.
It just provides a welcome message and simple usage instructions.
"""

from dex.tools import ToolBase, get_tool_names
from dex.utils.Exceptions import Error


# This is a special "tool" that is run when no subtool has been specified on
# the command line. Its only job is to provide useful usage info.
class Tool(ToolBase):
    """Welcome to DExTer (Debugging Experience Tester).
    Please choose a subtool from the list below.  Use 'dexter.py help' for more
    information.
    """

    @property
    def name(self):
        return 'DExTer'

    def add_tool_arguments(self, parser, defaults):
        parser.description = Tool.__doc__
        parser.add_argument(
            'subtool',
            choices=[t for t in get_tool_names() if not t.endswith('-')],
            nargs='?',
            help='name of subtool')
        parser.add_argument(
            'subtool_options',
            metavar='subtool-options',
            nargs='*',
            help='subtool specific options')

    def handle_options(self, defaults):
        if not self.context.options.subtool:
            raise Error('<d>no subtool specified</>\n\n{}\n'.format(
                self.parser.format_help()))

    def go(self):
        return 1
