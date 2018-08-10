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
"""Communication via the Windows COM interface."""

import inspect
import time
import sys

# pylint: disable=import-error
import win32com.client as com
import win32api
# pylint: enable=import-error

from dex.utils.Exceptions import LoadDebuggerException

_com_error = com.pywintypes.com_error  # pylint: disable=no-member


def get_file_version(file_):
    try:
        info = win32api.GetFileVersionInfo(file_, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return '.'.join(
            str(s) for s in [
                win32api.HIWORD(ms),
                win32api.LOWORD(ms),
                win32api.HIWORD(ls),
                win32api.LOWORD(ls)
            ])
    except com.pywintypes.error:  # pylint: disable=no-member
        return 'no versioninfo present'


def _handle_com_error(e):
    exc = sys.exc_info()
    msg = win32api.FormatMessage(e.hresult)
    try:
        msg = msg.decode('CP1251')
    except AttributeError:
        pass
    msg = msg.strip()
    return msg, exc


class ComObject(object):
    """Wrap a raw Windows COM object in a class that implements auto-retry of
    failed calls.
    """

    def __init__(self, raw):
        assert not isinstance(raw, ComObject), raw
        self.__dict__['raw'] = raw

    def __str__(self):
        return self._call(self.raw.__str__)

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        return self._call(self.raw.__getattr__, key)

    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        self._call(self.raw.__setattr__, key, val)

    def __getitem__(self, key):
        return self._call(self.raw.__getitem__, key)

    def __setitem__(self, key, val):
        self._call(self.raw.__setitem__, key, val)

    def __call__(self, *args):
        return self._call(self.raw, *args)

    @classmethod
    def _call(cls, fn, *args):
        """COM calls tend to randomly fail due to thread sync issues.
        The Microsoft recommended solution is to set up a message filter object
        to automatically retry failed calls, but this seems prohibitively hard
        from python, so this is a custom solution to do the same thing.
        All COM accesses should go through this function.
        """
        ex = AssertionError("this should never be raised!")

        assert (inspect.isfunction(fn) or inspect.ismethod(fn)
                or inspect.isbuiltin(fn)), (fn, type(fn))
        retries = ([0] * 50) + ([1] * 5)
        for r in retries:
            try:
                try:
                    result = fn(*args)
                    if inspect.ismethod(result) or 'win32com' in str(
                            result.__class__):
                        result = ComObject(result)
                    return result
                except _com_error as e:
                    msg, _ = _handle_com_error(e)
                    e = WindowsError(msg)  # pylint: disable=undefined-variable
                    raise e
            except (AttributeError, TypeError, OSError) as e:
                ex = e
                time.sleep(r)
        raise ex


class DTE(ComObject):
    def __init__(self, class_string):
        try:
            super(DTE, self).__init__(com.DispatchEx(class_string))
        except _com_error as e:
            msg, exc = _handle_com_error(e)
            raise LoadDebuggerException(
                '{} [{}]'.format(msg, class_string), orig_exception=exc)
