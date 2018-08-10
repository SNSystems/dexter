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
"""Create/set a temporary working directory for some operations."""

import os
import shutil
import tempfile
import time

from dex.utils.Exceptions import Error


class WorkingDirectory(object):
    def __init__(self, context, *args, **kwargs):
        self.context = context
        self.orig_cwd = os.getcwd()

        dir_ = kwargs.get('dir', None)
        if dir_ and not os.path.isdir(dir_):
            os.makedirs(dir_)
        self.path = tempfile.mkdtemp(*args, **kwargs)

    def __enter__(self):
        os.chdir(self.path)
        return self

    def __exit__(self, *args):
        os.chdir(self.orig_cwd)
        if self.context.options.save_temps:
            self.context.o.blue('"{}" left in place [--save-temps]\n'.format(
                self.path))
            return

        exception = AssertionError('should never be raised')
        for _ in range(100):
            try:
                shutil.rmtree(self.path)
                return
            except OSError as e:
                exception = e
                time.sleep(0.1)
        raise Error(exception)
