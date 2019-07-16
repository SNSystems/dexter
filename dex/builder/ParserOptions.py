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
"""Command line options for subtools that use the builder component."""

import os

from dex.tools import Context
from dex.utils import is_native_windows


def _find_build_scripts():
    """Finds build scripts in the 'scripts' subdirectory.

    Returns:
        { script_name (str): directory (str) }
    """
    try:
        return _find_build_scripts.cached
    except AttributeError:
        scripts_directory = os.path.join(os.path.dirname(__file__), 'scripts')
        if is_native_windows():
            scripts_directory = os.path.join(scripts_directory, 'windows')
        else:
            scripts_directory = os.path.join(scripts_directory, 'posix')
        assert os.path.isdir(scripts_directory), scripts_directory
        results = {}

        for f in os.listdir(scripts_directory):
            results[os.path.splitext(f)[0]] = os.path.abspath(
                os.path.join(scripts_directory, f))

        _find_build_scripts.cached = results
        return results


def add_builder_tool_arguments(parser):
    parser.add_argument('--binary',
                        metavar="<file>",
                        help='provide binary file to override --builder')

    parser.add_argument(
        '--builder',
        type=str,
        choices=sorted(_find_build_scripts().keys()),
        help='test builder to use')
    parser.add_argument(
        '--cflags', type=str, default='', help='compiler flags')
    parser.add_argument('--ldflags', type=str, default='', help='linker flags')


def handle_builder_tool_options(context: Context) -> str:
    return _find_build_scripts()[context.options.builder]
