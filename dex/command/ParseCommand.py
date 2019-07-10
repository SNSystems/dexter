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
import imp
import inspect
import os

from dex.command.CommandBase import CommandBase
from dex.utils.Exceptions import CommandParseError
from dex.command.commands.LTD import (
    And, Or, Not, Until, Expect, Eventually, Henceforth, Weak, Release,
    ExpectState, Next, After
)
from dex.dextIR import CommandIR


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


def get_command_object(commandIR: CommandIR):
    """Externally visible version of _safe_eval.  Only returns the Command
    object itself.
    """
    command = _eval_command(commandIR.raw_text, _get_valid_commands())
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
            command = _eval_command(to_eval, valid_commands)
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
