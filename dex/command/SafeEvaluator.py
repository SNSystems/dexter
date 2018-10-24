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

from dex.utils.Exceptions import UnsafeEval, InvalidCommandName


class SafeEvaluator(object):
    def __init__(self, valid_commands):
        self._valid_commands = valid_commands

    @staticmethod
    def _raise_syntax_error(command_node, syntax_error, command_text):
        """Clean interface for raising syntax errors
        """
        location = ('', command_node.lineno, command_node.col_offset + 1,
                    command_text)
        raise SyntaxError(syntax_error, location)

    @staticmethod
    def _get_as_module(command_as_text):
        """Parse the command text and interpret as a python module and return
           the result.
        """
        as_module = ast.parse(command_as_text)
        return as_module

    @staticmethod
    def _get_as_expressions(as_module):
        """Break a python module down into it's smaller parts, it's assumed
           a dexter command will only consist of expressions
        """
        if not isinstance(as_module, ast.Module):
            raise UnsafeEval(as_module, 'expected module')
        as_expressions = ast.iter_child_nodes(as_module)
        return as_expressions

    @staticmethod
    def _get_as_command_calls(as_expression):
        """Break a python expression down into it's constituent calls, at this
           moment it's possible to write DexWatch(...) + DexWatch(...) in test
           cases. return the resulting calls.
        """
        if not isinstance(as_expression, ast.Expr):
            raise UnsafeEval(as_expression, 'invalid expression')
        as_calls = ast.iter_child_nodes(as_expression)
        return as_calls

    @staticmethod
    def _split_call(as_call):
        """Split a python function call down into its function name object
           and arguments and return the results.
        """
        if not isinstance(as_call, ast.Call):
            raise UnsafeEval(as_call, 'expected a call')
        as_call_and_args = (list)(ast.iter_child_nodes(as_call))
        call = as_call_and_args[0]
        args = as_call_and_args[1:]
        return call, args

    @staticmethod
    def _get_name_as_string(command_name):
        """Attempt to access the 'raw' string value for a command's name
           and return the result.
        """
        try:
            as_string = command_name.id
        except AttributeError:
            raise UnsafeEval(command_name, 'invalid syntax')
        return as_string

    @staticmethod
    def _check_valid_command_name(command_name, valid_commands):
        """Check the command_name (a string at this point) is contained
           in the valid list of commands provided.
        """
        if command_name not in valid_commands:
            syntax_error = 'expected a call to '
            syntax_error += "{}".format(', '.join(valid_commands))
            raise InvalidCommandName(syntax_error)

    @staticmethod
    def _check_valid_arguments(command_args):
        """Check arguments can be evaluated correctly. The special case
           of keyword=<value> pairs is also handled.
        """
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

    def _check_valid_call_and_get_name(self, call):
        """Check the command call is valid, returns the string representation
           of the calls name for returning in evaluate_command.
        """
        command_name, command_args = self._split_call(call)
        try:
            name_as_string = self._get_name_as_string(command_name)
            self._check_valid_command_name(name_as_string,
                                           self._valid_commands)
            self._check_valid_arguments(command_args)
        except AttributeError:
            raise UnsafeEval(command_name, "invalid syntax")
        except InvalidCommandName as e:
            raise UnsafeEval(call, e.syntax_error)
        return name_as_string

    def evaluate_command(self, command_text):
        """Takes a string that should contain a valid DexTer command. The
           command is checked for validity against the valid commands
        """
        try:
            command_as_module = self._get_as_module(command_text)
            for expression in self._get_as_expressions(command_as_module):
                for call in self._get_as_command_calls(expression):
                    command_name = self._check_valid_call_and_get_name(call)
        except UnsafeEval as e:
            self._raise_syntax_error(e.command_node, e.syntax_error,
                                     command_text)
        # eval can modify the contents of this dict so only pass a copy.
        valid_commands_copy = self._valid_commands.copy()
        # pylint: disable=eval-used
        return (command_name, eval(command_text, valid_commands_copy))
        # pylint: enable=eval-used
