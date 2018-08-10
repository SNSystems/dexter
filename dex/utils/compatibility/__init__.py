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
"""Python 2/3 compatibility interface.
Provides a limited set of interfaces for constructs that are incompatible
between versions.

In most cases, this just makes use of the 'six' module, but we may attempt to
to phase out our reliance on it in future so all calls should be forwarded
through this module.
"""

try:
    from six import add_metaclass
    from six import assertRaisesRegex
    from six import iteritems
    from six import PY3
    from six import string_types
    from six import StringIO
except ImportError:
    import sys
    import traceback

    sys.stderr.write('''\n{}\nmodule 'six' is required.\n'''
                     '''Try: "{}" -m pip install six\n\n'''.format(
                         traceback.format_exc(), sys.executable))
    raise SystemExit(1)

from dex.utils.compatibility.OpenCSV import open_csv
