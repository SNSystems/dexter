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

from collections import defaultdict

from dex.utils.Exceptions import CommandParseError

from dex.command.CommandBase import CommandBase
from dex.command.commands.DexExpectProgramState import DexExpectProgramState
from dex.command.commands.DexExpectStepKind import DexExpectStepKind
from dex.command.commands.DexExpectStepOrder import DexExpectStepOrder
from dex.command.commands.DexExpectWatchValue import DexExpectWatchValue
from dex.command.commands.DexLabel import DexLabel
from dex.command.commands.DexUnreachable import DexUnreachable
from dex.command.commands.DexWatch import DexWatch


def _get_valid_commands():
    return {
      DexExpectProgramState.get_name() : DexExpectProgramState,
      DexExpectStepKind.get_name() : DexExpectStepKind,
      DexExpectStepOrder.get_name() : DexExpectStepOrder,
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
    """Return a dict which merges valid_commands and subcommands for
       command_name.
    """
    subcommands = valid_commands[command_name].get_subcommands()
    if subcommands:
        return { **valid_commands, **subcommands }
    return valid_commands


def _eval_command(command_raw: str, valid_commands: dict) -> CommandBase:
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
            if dex_label.path == command.path and dex_label.eval() == command_arg:
                command.resolve_label(dex_label.get_as_pair())
    # labels for command should be resolved by this point.
    if command.has_labels():
        syntax_error = SyntaxError()
        syntax_error.filename = command.path
        syntax_error.lineno = command.lineno
        syntax_error.offset = 0
        syntax_error.text = command.__str__
        raise syntax_error


def _find_start_of_command(line, valid_commands) -> int:
    """Scan line for a valid command, return the index of the first character
    of the command and the command. Return -1 if no command is found.
    """
    for command in valid_commands:
        start = line.rfind(command)
        if start != -1:
            return start
    return -1


def _find_end_of_command(line, start, paren_balance) -> (int, int):
    """Return (end, paren_balance) where end is 1 + the index of the last char
    in the command or, if the parentheses are not balanced, the end of the line.
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


def _find_all_commands_in_file(path, file_lines, valid_commands):
    commands = defaultdict(dict)
    err = CommandParseError()
    err.filename = path
    paren_balance = 0
    for lineno, line in enumerate(file_lines):
        start = 0 # Index from which we start parsing
        lineno += 1  # Line numbers start at 1.
        err.lineno = lineno
        err.src = line.rstrip()

        # If parens are currently balanced we can look for a new command
        if paren_balance == 0:
            start = _find_start_of_command(line, valid_commands)
            if start == -1:
                continue

            command_name = _get_command_name(line[start:])
            command_lineno = lineno
            command_column = start + 1 # Column numbers start at 1.
            cmd_text_list = [command_name]
            start += len(command_name) # Start searching for parens after cmd.

        end, paren_balance = _find_end_of_command(line, start, paren_balance)
        # Add this text blob to the command
        cmd_text_list.append(line[start:end])

        # If the parens are unbalanced start reading the next line in an attempt
        # to find the end of the command.
        if paren_balance != 0:
            continue

        # Parens are balanced, we have a full command to evaluate.
        try:
            raw_text = "".join(cmd_text_list)
            command = _eval_command(raw_text, valid_commands)
            command_name = _get_command_name(raw_text)
            command.path = path
            command.lineno = lineno
            command.raw_text = raw_text
            resolve_labels(command, commands)
            assert (path, lineno) not in commands[command_name], (
                command_name, commands[command_name])
            commands[command_name][path, lineno] = command
        except SyntaxError as e:
            err.info = str(e.msg)
            err.caret = '{}<r>^</>'.format(
                ' ' * (command_column + e.offset - 1))
            raise err
        except TypeError as e:
            err.info = str(e).replace('__init__() ', '')
            err.caret = '{}<r>{}</>'.format(
                ' ' * (command_column), '^' * (len(err.src) - command_column))
            raise err

    if paren_balance != 0:
        err.info = (
            "Unbalanced parenthesis starting at line {} column {}".format(
                command_lineno, command_column + len(command_name)))
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
