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
"""Help tool."""

import imp
import textwrap

from dex.tools import ToolBase, get_tool_names, get_tools_directory, tool_main


class Tool(ToolBase):
    """Provides help info on subtools."""

    @property
    def name(self):
        return 'DExTer help'

    @property
    def _visible_tool_names(self):
        return [t for t in get_tool_names() if not t.endswith('-')]

    def add_tool_arguments(self, parser, defaults):
        parser.description = Tool.__doc__
        parser.add_argument(
            'tool',
            choices=self._visible_tool_names,
            nargs='?',
            help='name of subtool')

    def handle_options(self, defaults):
        pass

    @property
    def _default_text(self):
        s = '\n<b>The following subtools are available:</>\n\n'
        tools_directory = get_tools_directory()
        for tool_name in sorted(self._visible_tool_names):
            internal_name = tool_name.replace('-', '_')
            module_info = imp.find_module(internal_name, [tools_directory])
            tool_doc = imp.load_module(internal_name,
                                       *module_info).Tool.__doc__
            tool_doc = tool_doc.strip() if tool_doc else ''
            tool_doc = textwrap.fill(' '.join(tool_doc.split()), 80)
            s += '<g>{}</>\n{}\n\n'.format(tool_name, tool_doc)
        return s

    def go(self):
        if self.context.options.tool is None:
            self.context.o.auto(self._default_text)
            return 0

        tool_name = self.context.options.tool.replace('-', '_')
        tools_directory = get_tools_directory()
        module_info = imp.find_module(tool_name, [tools_directory])
        module = imp.load_module(tool_name, *module_info)
        return tool_main(self.context, module.Tool(self.context), ['--help'])
