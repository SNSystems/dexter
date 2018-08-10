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


def _expand_text_replacements(text, source_files, compiler_options,
                              linker_options, executable_file):

    source_files = [_quotify(f) for f in source_files]
    object_files = [
        _quotify('{}.o'.format(os.path.basename(f))) for f in source_files
    ]
    source_indexes = ['{:02d}'.format(i + 1) for i in range(len(source_files))]

    replacements = {}
    replacements['SOURCE_INDEXES'] = ' '.join(source_indexes)
    replacements['SOURCE_FILES'] = ' '.join(source_files)
    replacements['OBJECT_FILES'] = ' '.join(object_files)
    replacements['LINKER_OPTIONS'] = linker_options

    for i, _ in enumerate(source_files):
        index = source_indexes[i]
        replacements['SOURCE_FILE_{}'.format(index)] = source_files[i]
        replacements['OBJECT_FILE_{}'.format(index)] = object_files[i]
        replacements['COMPILER_OPTIONS_{}'.format(index)] = compiler_options[i]

    replacements['EXECUTABLE_FILE'] = executable_file

    try:
        return replacements, text.format(**replacements)
    except KeyError as e:
        raise BuildScriptException('could not expand variable {}.\n'
                                   'Available expansions are: {}'.format(
                                       e, ', '.join(
                                           sorted(replacements.keys()))))


def run_external_build_script(context, script_path, source_files,
                              compiler_options, linker_options,
                              executable_file):

    builderIR = BuilderIR(
        name=context.options.builder,
        cflags=compiler_options,
        ldflags=linker_options,
    )
    tmp_script_path = os.path.join(context.working_directory.path,
                                   os.path.basename(script_path))

    assert len(source_files) == len(compiler_options), (source_files,
                                                        compiler_options)

    with open(script_path, 'r') as fp:
        text = fp.read()

    try:
        replacements, text = _expand_text_replacements(
            text, source_files, compiler_options, linker_options,
            executable_file)
    except BuildScriptException as e:
        raise BuildScriptException('{}: {}'.format(script_path, e))

    with open(tmp_script_path, 'w') as fp:
        fp.write(text)

    os.chmod(tmp_script_path, os.stat(script_path).st_mode)

    env = dict(os.environ)
    env.update(replacements)
    try:
        with Timer('running build script'):
            process = subprocess.Popen(
                [tmp_script_path],
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
    def test_expand_text_replacements(self):
        text = ''
        source_files = ['a.a']
        compiler_options = ['-option1 value1']
        linker_options = '-optionX valueX'
        executable_file = 'exe.exe'

        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]

        self.assertEqual(result, '')

        text = '{SOURCE_FILES}'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'a.a')

        text = '{SOURCE_FILE_01}'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'a.a')

        text = '{SOURCE_FILE_02}'
        with self.assertRaises(BuildScriptException):
            _expand_text_replacements(text, source_files, compiler_options,
                                      linker_options, executable_file)

        text = '{COMPILER_OPTIONS_01}'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, '-option1 value1')

        text = '{COMPILER_OPTIONS_02}'
        with self.assertRaises(BuildScriptException):
            _expand_text_replacements(text, source_files, compiler_options,
                                      linker_options, executable_file)

        text = '{EXECUTABLE_FILE}'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'exe.exe')

        text = '{FOO}'
        with self.assertRaises(BuildScriptException):
            _expand_text_replacements(text, source_files, compiler_options,
                                      linker_options, executable_file)

        text = (
            'xx {SOURCE_FILE_01} yy {COMPILER_OPTIONS_01} zz {EXECUTABLE_FILE}'
        )
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx a.a yy -option1 value1 zz exe.exe')

        source_files = ['a.a', 'b.b']
        compiler_options = ['-option1 value1', '-option2 value2']

        text = 'xx {SOURCE_FILES} yy'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx a.a b.b yy')

        text = 'xx {SOURCE_FILE_01} yy {COMPILER_OPTIONS_01} zz'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx a.a yy -option1 value1 zz')

        text = 'xx {SOURCE_FILE_01} yy {COMPILER_OPTIONS_02} zz'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx a.a yy -option2 value2 zz')

        text = 'xx {SOURCE_FILE_02} yy {COMPILER_OPTIONS_01} zz'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx b.b yy -option1 value1 zz')

        text = 'xx {SOURCE_FILE_02} yy {COMPILER_OPTIONS_02} zz'
        result = _expand_text_replacements(text, source_files,
                                           compiler_options, linker_options,
                                           executable_file)[1]
        self.assertEqual(result, 'xx b.b yy -option2 value2 zz')
