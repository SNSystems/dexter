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

from copy import copy

from dex.dextIR import DextStepIter, StepIR
from dex.command.commands.LTD.internal.OperatorTypes import (
    BinaryOperator, UnaryOperator
)


class Not(UnaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        return not self.operand.eval(trace_iter)


class And(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        return self.lhs.eval(trace_iter) and self.rhs.eval(trace_iter)


class Or(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        return self.lhs.eval(trace_iter) or self.rhs.eval(trace_iter)


class Weak(BinaryOperator):
    """ Weak(p, q) == p must hold until q and q may never hold
    """
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        trace_iter = copy(trace_iter)
        while not trace_iter.at_end():
            result = self.rhs.eval(trace_iter)
            if result is True:
                return True
            else:
                result = self.lhs.eval(trace_iter)
                if result is False:
                    return False
            trace_iter.increment()
        return True


class Until(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    # [TODO] Consider renaming to reduce confusion with CommandBase
    def eval(self, trace_iter: DextStepIter):
        trace_iter = copy(trace_iter)
        while not trace_iter.at_end():
            result = self.rhs.eval(trace_iter)
            if result is True:
                return True
            else:
                result = self.lhs.eval(trace_iter)
                if result is False:
                    return False
            trace_iter.increment()
        return False

