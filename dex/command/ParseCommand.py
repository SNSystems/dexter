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
from dex.command.commands.DexExpectProgramState import DexExpectProgramState
from dex.command.commands.DexExpectStepKind import DexExpectStepKind
from dex.command.commands.DexExpectStepOrder import DexExpectStepOrder
from dex.command.commands.DexExpectWatchValue import DexExpectWatchValue
from dex.command.commands.DexUnreachable import DexUnreachable
from dex.command.commands.DexWatch import DexWatch


def _get_valid_commands():
    return {
      DexExpectProgramState.get_name() : DexExpectProgramState,
      DexExpectStepKind.get_name() : DexExpectStepKind,
      DexExpectStepOrder.get_name() : DexExpectStepOrder,
      DexExpectWatchValue.get_name() : DexExpectWatchValue,
      DexUnreachable.get_name() : DexUnreachable,
      DexWatch.get_name() : DexWatch
    }


def get_command_object(commandIR):
    """Externally visible version of _safe_eval.  Only returns the Command
    object itself.
    """
    valid_commands = _get_valid_commands()
    # pylint: disable=eval-used
    command = eval(commandIR.raw_text, valid_commands)
    # pylint: enable=eval-used
    command.path = commandIR.loc.path
    command.lineno = commandIR.loc.lineno
    return command


def _get_command_name(command_raw):
    """Return command name by splitting up DExTer command contained in
       command_raw on the first opening paranthesis and further stripping
       any potential leading or trailing whitespace.
    """
    command_name = command_raw.split('(', 1)[0].rstrip()
    return command_name


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
            # pylint: disable=eval-used
            command = eval(to_eval, valid_commands)
            # pylint: enable=eval-used
            command_name = _get_command_name(to_eval)
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
