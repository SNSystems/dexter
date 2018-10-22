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


class SafeEvaluator(object):
    def __init__(self, valid_commands):
        self._valid_commands = valid_commands

    @staticmethod
    def _raise_syntax_error(command_node, syntax_error, command_text):
        location = ('', command_node.lineno, command_node.col_offset + 1,
                    command_text)
        raise SyntaxError(syntax_error, location)

    @staticmethod
    def _get_as_module(command_as_text):
        as_module = ast.parse(command_as_text)
        return as_module

    @staticmethod
    def _get_as_expressions(as_module):
        if not isinstance(as_module, ast.Module):
            raise UnsafeEval(as_module, 'expected module')
        as_expression = ast.iter_child_nodes(as_module)
        return as_expression

    @staticmethod
    def _get_as_command_calls(as_expression):
        if not isinstance(as_expression, ast.Expr):
            raise UnsafeEval(as_expression, 'invalid expression')
        as_call = ast.iter_child_nodes(as_expression)
        return as_call

    @staticmethod
    def _split_call(as_call):
        if not isinstance(as_call, ast.Call):
            raise UnsafeEval(as_call, 'expected a call')
        as_call_and_args = (list)(ast.iter_child_nodes(as_call))
        call = as_call_and_args[0]
        args = as_call_and_args[1:]
        return call, args

    def _check_valid_command_name(self, command_name):
        try:
            if command_name.id not in self._valid_commands:
                syntax_error = 'expected a call to '
                syntax_error += "{}".format(', '.join(self._valid_commands))
                raise UnsafeEval(command_name, syntax_error)
        except AttributeError:
            raise UnsafeEval(command_name, 'invalid syntax')
        return

    @staticmethod
    def _check_valid_arguments(command_args):
        for argument_index, argument in enumerate(command_args):
            # if an argument is keyword=<value> get the value for evaluation.
            arg_value = argument.value if isinstance(argument,
                                                     ast.keyword) else argument
            try:
                ast.literal_eval(arg_value)
            except ValueError:
                # 1st argument is the 0th element.
                syntax_error = 'argument #{}'.format(argument_index + 1)
                syntax_error += ': expected literal value'
                raise UnsafeEval(arg_value, syntax_error)

    def evaluate_command(self, command_text):
        """Takes a string that should contain a valid DexTer command. The
           command is checked for validity against the valid commands
        """
        try:
            command_as_module = self._get_as_module(command_text)
            for expression in self._get_as_expressions(command_as_module):
                for call in self._get_as_command_calls(expression):
                    command_name, command_arguments = self._split_call(call)
                    self._check_valid_command_name(command_name)
                    self._check_valid_arguments(command_arguments)
        except UnsafeEval as e:
            self._raise_syntax_error(e.command_node, e.syntax_error,
                                     command_text)

        # eval can modify the contents of this dict so only pass a copy.
        valid_commands_copy = self._valid_commands.copy()
        # pylint: disable=eval-used
        return (command_name, eval(command_text, valid_commands_copy))
        # pylint: enable=eval-used
