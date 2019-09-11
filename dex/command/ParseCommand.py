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

import unittest
from copy import copy

from collections import defaultdict

from dex.utils.Exceptions import CommandParseError

from dex.command.CommandBase import CommandBase
from dex.command.commands.DexExpectProgramState import DexExpectProgramState
from dex.command.commands.DexExpectStepKind import DexExpectStepKind
from dex.command.commands.DexExpectStepOrder import DexExpectStepOrder
from dex.command.commands.DexExpectWatchType import DexExpectWatchType
from dex.command.commands.DexExpectWatchValue import DexExpectWatchValue
from dex.command.commands.DexLabel import DexLabel
from dex.command.commands.DexUnreachable import DexUnreachable
from dex.command.commands.DexWatch import DexWatch


def _get_valid_commands():
    """Return all top level DExTer test commands.

    Returns:
        { name (str): command (class) }
    """
    return {
      DexExpectProgramState.get_name() : DexExpectProgramState,
      DexExpectStepKind.get_name() : DexExpectStepKind,
      DexExpectStepOrder.get_name() : DexExpectStepOrder,
      DexExpectWatchType.get_name() : DexExpectWatchType,
      DexExpectWatchValue.get_name() : DexExpectWatchValue,
      DexLabel.get_name() : DexLabel,
      DexUnreachable.get_name() : DexUnreachable,
      DexWatch.get_name() : DexWatch
    }


def _get_command_name(command_raw: str) -> str:
    """Return command name by splitting up DExTer command contained in
    command_raw on the first opening paranthesis and further stripping
    any potential leading or trailing whitespace.
    """
    return command_raw.split('(', 1)[0].rstrip()


def _merge_subcommands(command_name: str, valid_commands: dict) -> dict:
    """Merge valid_commands and command_name's subcommands into a new dict.

    Returns:
        { name (str): command (class) }
    """
    subcommands = valid_commands[command_name].get_subcommands()
    if subcommands:
        return { **valid_commands, **subcommands }
    return valid_commands


def _eval_command(command_raw: str, valid_commands: dict) -> CommandBase:
    """Build a command object from raw text.

    Returns:
        A dexter command object.
    """
    command_name = _get_command_name(command_raw)
    valid_commands = _merge_subcommands(command_name, valid_commands)
    # pylint: disable=eval-used
    command = eval(command_raw, valid_commands)
    # pylint: enable=eval-used
    return command


def resolve_labels(command: CommandBase, commands: dict):
    """Attempt to resolve any labels in command"""
    dex_labels = commands['DexLabel']
    command_label_args = command.get_label_args()
    for command_arg in command_label_args:
        for dex_label in list(dex_labels.values()):
            if (dex_label.path == command.path and
                dex_label.eval() == command_arg):
                command.resolve_label(dex_label.get_as_pair())
    # labels for command should be resolved by this point.
    if command.has_labels():
        syntax_error = SyntaxError()
        syntax_error.filename = command.path
        syntax_error.lineno = command.lineno
        syntax_error.offset = 0
        syntax_error.msg = 'Unresolved labels'
        for label in command.get_label_args():
            syntax_error.msg += ' \'' + label + '\''
        raise syntax_error


def _find_start_of_command(line, valid_commands) -> int:
    """Scan `line` for a string matching any key in `valid_commands`.

    Commands escaped with `\` (E.g. `\DexLabel('a')`) are ignored.

    Returns:
        int: the index of the first character of the matching string in `line`
        or -1 if no command is found.
    """
    for command in valid_commands:
        start = line.rfind(command)
        if start != -1:
            # Ignore escaped '\' commands.
            if start > 0 and line[start-1] == '\\':
                continue
            return start
    return -1


def _find_end_of_command(line, start, paren_balance) -> (int, int):
    """Find the end of a command by looking for balanced parentheses.

    Args:
        line (str): String to scan.
        start (int): Index into `line` to start looking.
        paren_balance(int): paren_balance after previous call.

    Note:
        On the first call `start` should point at the opening parenthesis and
        `paren_balance` should be set to 0. Subsequent calls should pass in the
        returned `paren_balance`.

    Returns:
        ( end (int), paren_balance (int) )
        Where end is 1 + the index of the last char in the command or, if the
        parentheses are not balanced, the end of the line.

        paren_balance will be 0 when the parentheses are balanced.
    """
    for end in range(start, len(line)):
        ch = line[end]
        if ch == '(':
            paren_balance += 1
        elif ch == ')':
            paren_balance -=1
        if paren_balance == 0:
            break
    end += 1
    return (end, paren_balance)


class TextPoint():
    def __init__(self, line, char):
        self.line = line
        self.char = char

    def get_lineno(self):
        return self.line + 1

    def get_column(self):
        return self.char + 1


def format_parse_err(msg: str, path: str, lines: list, point: TextPoint) -> CommandParseError:
    err = CommandParseError()
    err.filename = path
    err.src = lines[point.line].rstrip()
    err.lineno = point.get_lineno()
    err.info = msg
    err.caret = '{}<r>^</>'.format(' ' * (point.char))
    return err


def _find_all_commands_in_file(path, file_lines, valid_commands):
    commands = defaultdict(dict)
    paren_balance = 0
    region_start = TextPoint(0, 0)
    for region_start.line, line in enumerate(file_lines):
        region_start.char = 0

        # If parens are currently balanced we can look for a new command
        if paren_balance == 0:
            region_start.char = _find_start_of_command(line, valid_commands)
            if region_start.char == -1:
                continue

            command_name = _get_command_name(line[region_start.char:])
            cmd_point = copy(region_start)
            cmd_text_list = [command_name]
            region_start.char += len(command_name) # Start searching for parens after cmd.

        end, paren_balance = _find_end_of_command(line, region_start.char, paren_balance)
        # Add this text blob to the command
        cmd_text_list.append(line[region_start.char:end])

        # If the parens are unbalanced start reading the next line in an attempt
        # to find the end of the command.
        if paren_balance != 0:
            continue

        # Parens are balanced, we have a full command to evaluate.
        try:
            raw_text = "".join(cmd_text_list)
            command = _eval_command(raw_text, valid_commands)
            command.path = path
            command.lineno = cmd_point.get_lineno()
            command.raw_text = raw_text
            resolve_labels(command, commands)
            assert (path, cmd_point.get_lineno()) not in commands[command_name], (
                command_name, commands[command_name])
            commands[command_name][path, cmd_point.get_lineno()] = command
        except SyntaxError as e:
            # This err should point to the problem line.
            err_point = copy(cmd_point)
            # To e the command start is the absolute start, so use as offset.
            err_point.line += e.lineno - 1 # e.lineno is a position, not index.
            err_point.char += e.offset - 1 # e.offset is a position, not index.
            raise format_parse_err(e.msg, path, file_lines, err_point)
        except TypeError as e:
            # This err should always point to the end of the command name.
            err_point = copy(cmd_point)
            err_point.char += len(command_name)
            raise format_parse_err(str(e), path, file_lines, err_point)

    if paren_balance != 0:
        # This err should always point to the end of the command name.
        err_point = copy(cmd_point)
        err_point.char += len(command_name)
        msg = "Unbalanced parenthesis starting here"
        raise format_parse_err(msg, path, file_lines, err_point)
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
    class MockCmd(CommandBase):
        """A mock DExTer command for testing parsing.

        Args:
            value (str): Unique name for this instance.
        """

        def __init__(self, *args):
           self.value = args[0]

        def get_name():
            return __class__.__name__

        def eval(this):
            pass


    def __init__(self, *args):
        super().__init__(*args)

        self.valid_commands = {
            TestParseCommand.MockCmd.get_name() : TestParseCommand.MockCmd
        }


    def _find_all_commands_in_lines(self, lines):
        """Use DExTer parsing methods to find all the mock commands in lines.

        Returns:
            { cmd_name: { (path, line): command_obj } }
        """
        return _find_all_commands_in_file(__file__, lines, self.valid_commands)


    def _find_all_mock_values_in_lines(self, lines):
        """Use DExTer parsing methods to find all mock command values in lines.

        Returns:
            values (list(str)): MockCmd values found in lines.
        """
        cmds = self._find_all_commands_in_lines(lines)
        mocks = cmds.get(TestParseCommand.MockCmd.get_name(), None)
        return [v.value for v in mocks.values()] if mocks else []


    def test_parse_inline(self):
        """Commands can be embedded in other text."""

        lines = [
            'MockCmd("START") Lorem ipsum dolor sit amet, consectetur\n',
            'adipiscing elit, MockCmd("EMBEDDED") sed doeiusmod tempor,\n',
            'incididunt ut labore et dolore magna aliqua.\n'
        ]

        values = self._find_all_mock_values_in_lines(lines)

        self.assertTrue('START' in values)
        self.assertTrue('EMBEDDED' in values)


    def test_parse_multi_line_comment(self):
        """Multi-line commands can embed comments."""

        lines = [
            'Lorem ipsum dolor sit amet, consectetur\n',
            'adipiscing elit, sed doeiusmod tempor,\n',
            'incididunt ut labore et MockCmd(\n',
            '    "WITH_COMMENT" # THIS IS A COMMENT\n',
            ') dolore magna aliqua. Ut enim ad minim\n',
        ]

        values = self._find_all_mock_values_in_lines(lines)

        self.assertTrue('WITH_COMMENT' in values)

    def test_parse_empty(self):
        """Empty files are silently ignored."""

        lines = []
        values = self._find_all_mock_values_in_lines(lines)
        self.assertTrue(len(values) == 0)

    # [TODO]: Fix parsing so this passes.
    @unittest.expectedFailure
    def test_parse_whitespace(self):
        """Try to emulate python whitespace rules"""

        lines = [
            # Good
            'MockCmd("NONE")\n',
            'MockCmd    ("SPACE")\n',
            'MockCmd\t\t("TABS")\n',
            'MockCmd(    "ARG_SPACE"    )\n',
            'MockCmd(\t\t"ARG_TABS"\t\t)\n',
            'MockCmd(\n',
            '"CMD_PAREN_LF")\n',
            # Bad
            'MockCmd\n',
            '("XFAIL_CMD_LF_PAREN")\n',
        ]

        values = self._find_all_mock_values_in_lines(lines)

        self.assertTrue('NONE' in values)
        self.assertTrue('SPACE' in values)
        self.assertTrue('TABS' in values)
        self.assertTrue('ARG_SPACE' in values)
        self.assertTrue('ARG_TABS' in values)
        self.assertTrue('CMD_PAREN_LF' in values)

        self.assertFalse('XFAIL_CMD_LF_PAREN' in values)


    # [TODO]: Fix parsing so this passes.
    @unittest.expectedFailure
    def test_parse_share_line(self):
        """More than one command can appear on one line."""

        lines = [
            'MockCmd("START") MockCmd("CONSECUTIVE") words '
                'MockCmd("EMBEDDED") more words\n'
        ]

        values = self._find_all_mock_values_in_lines(lines)

        self.assertTrue('START' in values)
        self.assertTrue('CONSECUTIVE' in values)
        self.assertTrue('EMBEDDED' in values)


    def test_parse_escaped(self):
        """Escaped commands are ignored."""

        lines = [
            'words \MockCmd("IGNORED") words words words\n'
        ]

        values = self._find_all_mock_values_in_lines(lines)

        self.assertFalse('IGNORED' in values)
