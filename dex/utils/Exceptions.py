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
"""Provides Dexter-specific exception types."""


class Dexception(Exception):
    """All dexter-specific exceptions derive from this."""
    pass


class Error(Dexception):
    """Error.  Prints 'error: <message>' without a traceback."""
    pass


class DebuggerException(Dexception):
    """Any error from using the debugger."""

    def __init__(self, msg, orig_exception=None):
        super(DebuggerException, self).__init__(msg)
        self.msg = msg
        self.orig_exception = orig_exception

    def __str__(self):
        return str(self.msg)


class LoadDebuggerException(DebuggerException):
    """If specified debugger cannot be loaded."""
    pass


class NotYetLoadedDebuggerException(LoadDebuggerException):
    """If specified debugger has not yet been attempted to load."""

    def __init__(self):
        super(NotYetLoadedDebuggerException, self).__init__(
            'not loaded', orig_exception=None)


class CommandParseError(Dexception):
    """If a command instruction cannot be successfully parsed."""

    def __init__(self, *args, **kwargs):
        super(CommandParseError, self).__init__(*args, **kwargs)
        self.filename = None
        self.lineno = None
        self.info = None
        self.src = None
        self.caret = None


class SrInitError(Dexception):
    """If a serialized object cannot be initialized correctly."""
    pass


class ToolArgumentError(Dexception):
    """If a tool argument is invalid."""
    pass


class BuildScriptException(Dexception):
    """If there is an error in a build script file."""

    def __init__(self, *args, **kwargs):
        self.script_error = kwargs.pop('script_error', None)
        super(BuildScriptException, self).__init__(*args, **kwargs)


class HeuristicException(Dexception):
    """If there was a problem with the heuristic."""
    pass


class ImportDextIRException(Dexception):
    """If there was a problem importing the dextIR json file."""
    pass


class UnsafeEval(Dexception):
    """If there was a problem safely evaluating a dexter command."""

    def __init__(self, command_node, syntax_error):
        self.command_node = command_node
        self.syntax_error = syntax_error
        super(UnsafeEval, self).__init__(command_node, syntax_error)
