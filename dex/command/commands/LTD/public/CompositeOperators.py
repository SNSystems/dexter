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

from dex.dextIR import DextStepIter, StepIR
from dex.command.commands.LTD.internal.OperatorTypes import (
    BinaryOperator, UnaryOperator
)
from dex.command.commands.LTD.public.BasicOperators import (
    And, Or, Not, Until, Weak
)


class Eventually(UnaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.proposition = Until(True, self.operand)

    def eval(self, trace_iter: DextStepIter):
        return self.proposition.eval(trace_iter)

    def __str__(self):
        return "{} is {}".format(
            self.__class__.__name__, self.proposition.__str__())

    def __repr__(self):
        return self.__str__()


class Release(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.proposition = Weak(self.rhs, And(self.rhs, self.lhs))

    def eval(self, trace_iter: DextStepIter):
        return  self.proposition.eval(trace_iter)

    def __str__(self):
        return "{} is {}".format(
            self.__class__.__name__, self.proposition.__str__())

    def __repr__(self):
        return self.__str__()


class Henceforth(UnaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.proposition = Release(False, self.operand)

    def eval(self, trace_iter: DextStepIter):
        return self.proposition.eval(trace_iter)

    def __str__(self):
        return "{} is {}".format(
            self.__class__.__name__, self.proposition.__str__())

    def __repr__(self):
        return self.__str__()
