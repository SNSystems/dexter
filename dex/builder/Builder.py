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
"""Deals with the processing execution of shell or batch build scripts."""

import os
import subprocess
import unittest

from dex.dextIR import BuilderIR
from dex.utils import Timer
from dex.utils.Exceptions import BuildScriptException


def _quotify(text):
    if '"' in text or ' ' not in text:
        return text
    return '"{}"'.format(text)


def _get_script_environment(source_files, compiler_options,
                            linker_options, executable_file):

    source_files = [_quotify(f) for f in source_files]
    object_files = [
        _quotify('{}.o'.format(os.path.basename(f))) for f in source_files
    ]
    source_indexes = ['{:02d}'.format(i + 1) for i in range(len(source_files))]

    env_variables = {}
    env_variables['SOURCE_INDEXES'] = ' '.join(source_indexes)
    env_variables['SOURCE_FILES'] = ' '.join(source_files)
    env_variables['OBJECT_FILES'] = ' '.join(object_files)
    env_variables['LINKER_OPTIONS'] = linker_options

    for i, _ in enumerate(source_files):
        index = source_indexes[i]
        env_variables['SOURCE_FILE_{}'.format(index)] = source_files[i]
        env_variables['OBJECT_FILE_{}'.format(index)] = object_files[i]
        env_variables['COMPILER_OPTIONS_{}'.format(index)] = compiler_options[i]

    env_variables['EXECUTABLE_FILE'] = executable_file

    return env_variables


def run_external_build_script(context, script_path, source_files,
                              compiler_options, linker_options,
                              executable_file):
    """Build an executable using a builder script.

    The executable is saved to `context.working_directory.path`.

    Returns:
        ( stdout (str), stderr (str), builder (BuilderIR) )
    """

    builderIR = BuilderIR(
        name=context.options.builder,
        cflags=compiler_options,
        ldflags=linker_options,
    )
    assert len(source_files) == len(compiler_options), (source_files,
                                                        compiler_options)

    script_environ = _get_script_environment(source_files, compiler_options,
                                             linker_options, executable_file)
    env = dict(os.environ)
    env.update(script_environ)
    try:
        with Timer('running build script'):
            process = subprocess.Popen(
                [script_path],
                cwd=context.working_directory.path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = process.communicate()
            returncode = process.returncode
        if returncode != 0:
            raise BuildScriptException(
                '{}: failed with returncode {}.\nstdout:\n{}\n\nstderr:\n{}\n'.
                format(script_path, returncode, out, err),
                script_error=err)
        return out.decode('utf-8'), err.decode('utf-8'), builderIR
    except OSError as e:
        raise BuildScriptException('{}: {}'.format(e.strerror, script_path))


class TestBuilder(unittest.TestCase):
    def test_get_script_environment(self):
        source_files = ['a.a', 'b.b']
        compiler_options = ['-option1 value1', '-option2 value2']
        linker_options = '-optionX valueX'
        executable_file = 'exe.exe'
        env = _get_script_environment(source_files, compiler_options,
                                      linker_options, executable_file)

        assert env['SOURCE_FILES'] == 'a.a b.b'
        assert env['OBJECT_FILES'] == 'a.a.o b.b.o'

        assert env['SOURCE_INDEXES'] == '01 02'
        assert env['LINKER_OPTIONS'] == '-optionX valueX'

        assert env['SOURCE_FILE_01'] == 'a.a'
        assert env['SOURCE_FILE_02'] == 'b.b'

        assert env['OBJECT_FILE_01'] == 'a.a.o'
        assert env['OBJECT_FILE_02'] == 'b.b.o'

        assert env['EXECUTABLE_FILE'] == 'exe.exe'

        assert env['COMPILER_OPTIONS_01'] == '-option1 value1'
        assert env['COMPILER_OPTIONS_02'] == '-option2 value2'
