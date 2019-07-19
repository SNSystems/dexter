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
"""Base classes and utilities required for LTD propositions."""

import abc

from dex.dextIR import DextStepIter


class Proposition:
    """Base class for all LTD propositions."""

    @abc.abstractmethod
    def eval(self, trace_iter: DextStepIter) -> bool:
        """Verify that this proposition holds.

        `trace_iter` must be copied if it is going to be modified
        (e.g. incremented). It is okay to increment and blindly pass on because:

        You MUST check `not trace_iter.at_end()` before using
        `trace_iter.dereference()` to get the current debugger step.

        Args:
            trace_iter: Debugger steps to verify.

        Returns:
            True if the proposition holds.
        """
        pass


class Composite:
    """Interface for composite LTD operators.

    Operators using this interface need not define an `eval()`. You must call
    `set_proposition` once to bind the composite proposition.

    set_proposition adds the attribute `proposition` to this object.
    """

    def eval(self, trace_iter: DextStepIter):
        return  self.proposition.eval(trace_iter)

    def set_proposition(self, p: Proposition):
        self.proposition = p


class Boolean(Proposition):
    """A wrapper around `bool` type for LTD expressions.

    Arg list:
        param1 (bool): The value to wrap.
    """

    def __init__(self, *args):
        if len(args) != 1:
            raise TypeError('Expected exactly one arg')
        if not isinstance(args[0], bool):
            raise TypeError('Boolean.__init__() requires bool arg')

        self.value = args[0]

    def eval(self, trace_iter: DextStepIter) -> bool:
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


def load_proposition_arg(arg) -> Proposition:
    """Validate a `Proposition` argument.

    Promotes `arg` from `bool` type to `Boolean` which is a valid proposition.

    Raises:
        TypeError: arg is not a `bool` or `Proposition`.

    Returns:
        The proposition.
    """
    if isinstance(arg, bool):
        arg = Boolean(arg)
    elif not isinstance(arg, Proposition):
        raise TypeError('Arg is not a proposition: {}'.format(self.operand))
    return arg
