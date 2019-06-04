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
"""Parse a DExTer command. In particular, ensure that only a very limited
subset of Python is allowed, in order to prevent the possibility of unsafe
Python code being embedded within DExTer commands.
"""

import ast
from collections import defaultdict
import imp
import inspect
import os
import unittest

from dex.command.CommandBase import CommandBase
from dex.utils.Exceptions import CommandParseError


def _get_valid_commands():
    """Search the commands subdirectory for any classes which are subclasses of
    CommandBase and return a dict in the form of {name: class}.
    """
    try:
        return _get_valid_commands.cached
    except AttributeError:
        commands_directory = os.path.join(
            os.path.dirname(__file__), 'commands')
        potential_modules = [
            os.path.splitext(f)[0] for f in os.listdir(commands_directory)
        ]

        commands = {}
        for m in potential_modules:
            try:
                module_info = imp.find_module(m, [commands_directory])
                module = imp.load_module(m, *module_info)
            except ImportError:
                continue

            commands.update({
                c[0]: c[1]
                for c in inspect.getmembers(module, inspect.isclass)
                if c[1] != CommandBase and issubclass(c[1], CommandBase)
            })
        _get_valid_commands.cached = commands
        return commands


def _safe_eval(command_text, valid_commands):  # noqa
    """Before evaling the command check that it's not doing anything
    potentially unsafe.  It should be a call only to one of our commands and
    should only contain literal values as arguments.
    """
    module = ast.parse(command_text)
    assert isinstance(module, ast.Module), type(module)

    command_name = None
    for node1 in ast.iter_child_nodes(module):
        if not isinstance(node1, ast.Expr):
            location = ('', node1.lineno, node1.col_offset + 1, command_text)
            raise SyntaxError('invalid expression', location)

        for node2 in ast.iter_child_nodes(node1):
            location = ('', node2.lineno, node2.col_offset + 1, command_text)

            if not isinstance(node2, ast.Call):
                raise SyntaxError('expected a call', location)

            children = list(ast.iter_child_nodes(node2))
            try:
                command_name = children[0].id
            except AttributeError:
                location = ('', children[0].lineno, children[0].col_offset + 1,
                            command_text)
                raise SyntaxError('invalid syntax', location)

            if command_name not in valid_commands:
                raise SyntaxError(
                    'expected a call to {}'.format(', '.join(valid_commands)),
                    location)

            children = children[1:]
            for i, node3 in enumerate(children):
                if isinstance(node3, ast.keyword):
                    node3 = node3.value
                location = ('', node3.lineno, node3.col_offset + 1,
                            command_text)

                try:
                    ast.literal_eval(node3)
                except ValueError:
                    raise SyntaxError(
                        'argument #{}: expected literal value'.format(i + 1),
                        location)

    # eval can modify the contents of this dict so only pass a copy.
    valid_commands_copy = valid_commands.copy()
    # pylint: disable=eval-used
    return (command_name, eval(command_text, valid_commands_copy))
    # pylint: enable=eval-used


def get_command_object(commandIR):
    """Externally visible version of _safe_eval.  Only returns the Command
    object itself.
    """
    command = _safe_eval(commandIR.raw_text, _get_valid_commands())[1]
    command.path = commandIR.loc.path
    command.lineno = commandIR.loc.lineno
    return command


def _find_all_commands_in_file(path, file_lines, valid_commands):
    commands = defaultdict(dict)

    err = CommandParseError()
    err.filename = path

    for lineno, line in enumerate(file_lines):
        lineno += 1  # Line numbering convention starts at 1.
        err.lineno = lineno
        err.src = line.rstrip()

        for command in valid_commands:
            column = line.rfind(command)
            if column != -1:
                break
        else:
            continue

        to_eval = line[column:].rstrip()
        try:
            command_name, command = _safe_eval(to_eval, valid_commands)
            command.path = path
            command.lineno = lineno
            command.raw_text = to_eval
            assert (path, lineno) not in commands[command_name], (
                command_name, commands[command_name])
            commands[command_name][path, lineno] = command
        except SyntaxError as e:
            err.info = str(e.msg)
            err.caret = '{}<r>^</>'.format(' ' * (column + e.offset - 1))
            raise err
        except TypeError as e:
            err.info = str(e).replace('__init__() ', '')
            err.caret = '{}<r>{}</>'.format(' ' * (column),
                                            '^' * (len(err.src) - column))
            raise err

    return dict(commands)


def find_all_commands(source_files):
    commands = defaultdict(dict)
    valid_commands = _get_valid_commands()
    for source_file in source_files:
        with open(source_file) as fp:
            lines = fp.readlines()
        file_commands = _find_all_commands_in_file(source_file, lines,
                                                   valid_commands)
        for command_name in file_commands:
            commands[command_name].update(file_commands[command_name])

    return dict(commands)


class TestParseCommand(unittest.TestCase):
    class MockBase(CommandBase):
        def __call__(self):
            pass

    class MockCommand1(MockBase):
        def __init__(self, *args):
            super(TestParseCommand.MockCommand1, self).__init__()
            if not args:
                raise TypeError('expected some args')

    class MockCommand2(MockBase):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            super(TestParseCommand.MockCommand2, self).__init__()
            if args:
                raise TypeError('did not expect any args')

    def test_safe_eval(self):
        valid_commands = {
            'MockCommand1': TestParseCommand.MockCommand1,
            'MockCommand2': TestParseCommand.MockCommand2
        }

        # Unknown string (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^expected a call \(, line 1\)$'):
            _safe_eval('MockCommand3', valid_commands)

        # Known command, but not a call (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^expected a call \(, line 1\)$'):
            _safe_eval('MockCommand1', valid_commands)

        # Python assignment (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid expression \(, line 1\)$'):
            _safe_eval('MockCommand3 = 3', valid_commands)

        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid expression \(, line 1\)$'):
            _safe_eval('MockCommand1 = 3', valid_commands)

        # Command expects args (invalid)
        with self.assertRaisesRegex(TypeError, r'^expected some args$'):
            _safe_eval('MockCommand1()', valid_commands)

        # Command expects args (valid)
        _safe_eval('MockCommand1(0)', valid_commands)
        _safe_eval('MockCommand1("abc")', valid_commands)

        # Command doesn't expect args (valid)
        _safe_eval('MockCommand2()', valid_commands)

        # Command receives named args (valid)
        _safe_eval('MockCommand2(x = 2)', valid_commands)

        # Command receives named args (invalid)
        with self.assertRaisesRegex(TypeError,
                               r" got an unexpected keyword argument 'x'$"):
            _safe_eval('MockCommand1(3, x = 2)', valid_commands)

        # Preceding characters (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid syntax \(<unknown>, line 1\)$'):
            _safe_eval('abc MockCommand2()', valid_commands)

        # Trailing characters (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid syntax \(<unknown>, line 1\)$'):
            _safe_eval('MockCommand2() abc', valid_commands)

        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid syntax \(<unknown>, line 1\)$'):
            _safe_eval('MockCommand2() MockCommand2()', valid_commands)

        # Second expression embedded (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               r'^invalid syntax \(<string>, line 1\)$'):
            _safe_eval('MockCommand2(); MockCommand2()', valid_commands)

        # Command expects args (invalid)
        with self.assertRaisesRegex(TypeError, r'^did not expect any args$'):
            _safe_eval('MockCommand2(1)', valid_commands)

        # Call unknown function (invalid)
        with self.assertRaisesRegex(
                SyntaxError,
                r'^expected a call to MockCommand[12], MockCommand[12]'
                r' \(, line 1\)$'):
            _safe_eval('MockCommand3()', valid_commands)

        # Unexpected EOF (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               (r'^unexpected EOF while parsing'
                                r' \(<unknown>, line 1\)$')):
            _safe_eval('MockCommand2(', valid_commands)

        for expression in [
                'MockCommand2()()',
                'MockCommand2()[]',
                'MockCommand2[]',
                'MockCommand2[]()',
                '[MockCommand2]()',
        ]:
            with self.assertRaisesRegex(
                    SyntaxError,
                    r'^invalid syntax \((<unknown>)?, line 1\)$'):
                _safe_eval(expression, valid_commands)

        # unsafe args (invalid)
        for expression in [
                'MockCommand1(MockCommand2())',
                'MockCommand1(foo)',
                'MockCommand2(foo=bar())',
                'MockCommand1(int(2))',
                'MockCommand1(str(1))',
                '''MockCommand1(eval('print("HACKED!")'))''',
        ]:
            with self.assertRaisesRegex(SyntaxError,
                                   (r'^argument #1: expected literal value'
                                    r' \(, line 1\)$')):
                _safe_eval(expression, valid_commands)

        # unsafe argument 2 (invalid)
        with self.assertRaisesRegex(SyntaxError,
                               (r'^argument #2: expected literal value'
                                r' \(, line 1\)$')):
            _safe_eval('MockCommand1(0, MockCommand2())', valid_commands)
