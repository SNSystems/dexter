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
from dex.command.commands.LTD.internal.Proposition import Proposition
from dex.command.commands.LTD.internal.OperatorTypes import (
    BinaryOperator, UnaryOperator
)

## For the demo we only allow the user to verify expressions.
class Expect(Proposition):
    def __init__(self, *args):
        if len(args) != 2:
            raise TypeError('expected exactly two args')

        self.var = args[0]
        self.value = args[1]

    def eval(self, trace_iter: DextStepIter):
        for expr, watch in trace_iter.dereference().watches.items():
            if self.var == expr:
                print("Expect({} == {}) and got {} == {}".format(self.var, self.value, expr, watch.value))
                return self.value == watch.value
        return False

    def __str__(self):
        return "Expect({} = {})".format(self.var, self.value)

    def __repr__(self):
        return self.__str__()
