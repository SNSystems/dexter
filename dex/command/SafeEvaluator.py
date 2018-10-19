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
"""Safely evaluate a DexTer command. Contruct a SafetyEvauluator object with a
   list of valid commands, then pass command text to have it evaluated safely.
"""

import ast

from dex.utils.Exceptions import UnsafeEval

class DexCommandSafeEvaluator(object):

    def __init__(self, valid_commands):
        self._valid_commands = valid_commands

    def _raise_exception_for(self, ast_node):
        location = ast_node('', ast_node.lineno, ast_node.col_offset + 1, )


    def _get_as_module(self, command_text):
        as_module = ast.parse(command_text)
        return as_module


    def _get_as_expression(self, command_as_module):
        if not isinstance(as_module, ast.Module):
            unsafe_exception = UnsafeEval(command_as_module)
        as_expression = ast.iter_child_nodes(command_as_module)
        return as_expression


    def _get_as_call_and_args(self, command_as_expression):
        if not isinstance(as_expression, ast.Expr):
            _raise_exception_for(command_as_module)


    def evaluate_command(self, command_text):
        """Takes a string that should contain a valid DexTer command. The
           command is checked for validity against the valid commands
        """
        command_as_module = self._get_as_module(command_text)
        for expressions in self._commands_as_expressions(command_as_module):
            for call_and_args in self._get_as_call_and_args(command_as_expressions):

