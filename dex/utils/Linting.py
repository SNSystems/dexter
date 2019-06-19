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
"""Use style and linting modules to self-check the quality of the DExTer code.
"""

import os
import sys

from io import StringIO

from dex.utils import PreserveAutoColors, Timer, warn


class _PreserveStreams(object):
    """Allow us to safely override sys.stdout and sys.stderr temporarily,
    restoring the original values at the end of the scope.
    (NOT THREAD SAFE)
    """

    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def __enter__(self):
        return self

    def __exit__(self, *args):
        sys.stdout = self.stdout
        sys.stderr = self.stderr


class _ChangeDir(object):
    """Change the current working directory for the duration of the scope.
    (NOT THREAD SAFE)
    """

    def __init__(self, path):
        self.path = path
        assert os.path.isdir(self.path), self.path
        self.orig = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)
        return self

    def __exit__(self, *args):
        os.chdir(self.orig)


def _warn(context, msg):
    warn(context, msg, '--lint={}'.format(context.options.lint))


def _run_pycodestyle(context):
    try:
        import pycodestyle
    except ImportError as e1:
        try:
            import pep8 as pycodestyle
        except ImportError as e2:
            _warn(context, 'could not run pycodestyle ({} / {})\n'.format(
                e1, e2))
            return True

    config_file = os.path.join(context.root_directory, '..', 'setup.cfg')
    assert os.path.isfile(config_file), config_file

    with PreserveAutoColors(context.o):
        context.o.auto_reds.extend([r': E\d+ '])
        context.o.auto_yellows.extend([r': W\d+ '])

        with _PreserveStreams():
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            pycodestyle.StyleGuide(config_file=config_file).check_files(
                paths=[context.root_directory])

            output = '\n'.join([sys.stdout.getvalue(),
                                sys.stderr.getvalue()]).strip()

            if output:
                context.o.green('\npycodestyle output:\n')
                context.o.auto('{}\n'.format(output))

            return not output


def _run_pylama(context):
    try:
        from pylama.main import check_path, parse_options
    except ImportError as e:
        _warn(context, 'could not run pylama ({})\n'.format(e))
        return True

    options = parse_options([os.path.join(context.root_directory, '..')])
    errors = check_path(options)

    if errors:
        context.o.green('\npylama output:\n')

        with PreserveAutoColors(context.o):
            context.o.auto_reds.extend([r': E\d+ '])
            context.o.auto_yellows.extend([r': W\d+ '])

            for e in errors:
                context.o.auto('{}:{}:{}: {}\n'.format(
                    os.path.join(e.filename), e.lnum, e.col, e.text))
        return False

    return True


def _run_yapf_check(context):
    try:
        from yapf.yapflib.yapf_api import FormatFile
    except ImportError as e:
        _warn(context, 'could not run yapf ({})\n'.format(e))
        return True

    ok = True
    for r, _, fs in os.walk(context.root_directory):
        if 'thirdparty' in r:
            continue

        for f in fs:
            if not f.endswith('.py'):
                continue

            path = os.path.join(r, f)
            _, _, changed = FormatFile(
                path,
                style_config=os.path.join(context.root_directory, '..',
                                          'setup.cfg'))
            if changed:
                if ok:
                    context.o.green('\nyapf-check output:\n')

                context.o.red(
                    '{}: yapf would change formatting\n'.format(path))
                ok = False

    if not ok:
        yapf_format = os.path.abspath(
            os.path.join(context.root_directory, '..', 'yapf-format.py'))
        assert os.path.isfile(yapf_format), yapf_format
        context.o.yellow('Please use "{}"\n'.format(yapf_format))

    return ok


def _run_pylint(context):
    try:
        from pylint.lint import Run
    except ImportError as e:
        _warn(context, 'could not run pylint ({})\n'.format(e))
        return True

    exit_code = 1

    with PreserveAutoColors(context.o):
        context.o.auto_reds.extend(['^[EF]:', r'^\*+'])
        context.o.auto_yellows.extend(['^Your code', '^[CRW]:'])

        with _PreserveStreams():
            try:
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                Run(args=[context.root_directory])
            except SystemExit as e:
                exit_code = e.code
            finally:
                if exit_code:
                    context.o.green('\npylint output:\n')
                    context.o.auto(sys.stdout.getvalue())
                    context.o.auto(sys.stderr.getvalue())

    return exit_code is 0


def _run_linter(context, fn):
    try:
        return fn(context)
    except Exception as e:  # pylint: disable=broad-except
        _warn(
            context, '{} failed: <r>[{}] {}</>'.format(fn.__name__,
                                                       type(e).__name__, e))

        if context.options.error_debug:
            raise

        return False


def linting_ok(context):
    ok = True
    with Timer('linting'):
        with _ChangeDir(os.path.join(context.root_directory, '..')):
            with Timer('pycodestyle'):
                ok = _run_linter(context, _run_pycodestyle) and ok

            if context.options.lint == 'full':
                with Timer('pylama'):
                    ok = _run_linter(context, _run_pylama) and ok

                with Timer('yapf-check'):
                    ok = _run_linter(context, _run_yapf_check) and ok

                with Timer('pylint'):
                    ok = _run_linter(context, _run_pylint) and ok

    return ok
