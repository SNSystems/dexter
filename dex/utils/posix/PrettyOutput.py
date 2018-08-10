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
"""Provides POSIX implementation of formatted/colored console output."""

from ..PrettyOutputBase import PrettyOutputBase, _lock


class PrettyOutput(PrettyOutputBase):
    def _color(self, text, color, stream, lock=_lock):
        """Use ANSI escape codes to provide color on Linux."""
        stream = self._set_valid_stream(stream)
        with lock:
            if stream.color_enabled:
                text = '\033[{}m{}\033[0m'.format(color, text)
            self._write(text, stream)

    def red_impl(self, text, stream=None, **kwargs):
        self._color(text, 91, stream, **kwargs)

    def yellow_impl(self, text, stream=None, **kwargs):
        self._color(text, 93, stream, **kwargs)

    def green_impl(self, text, stream=None, **kwargs):
        self._color(text, 92, stream, **kwargs)

    def blue_impl(self, text, stream=None, **kwargs):
        self._color(text, 96, stream, **kwargs)

    def default_impl(self, text, stream=None, **kwargs):
        self._color(text, 0, stream, **kwargs)
