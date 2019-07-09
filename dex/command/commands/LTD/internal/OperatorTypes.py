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

import abc
from dex.dextIR import DextStepIter
from dex.command.commands.LTD.internal.Proposition import (
    Proposition, Boolean, unwrap_LTD_arg
)

class UnaryOperator(Proposition):
    ## @@ implement a nice __rep__
    ## @@ implement a nice __str__ which prints a tree-like pattern.
    def __init__(self, *args):
        if len(args) != 1:
            raise TypeError('Expected exactly one arg')

        self.operand = unwrap_LTD_arg(args[0])

    def eval(self, trace_iter: DextStepIter) -> bool:
        pass

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.operand)


class BinaryOperator(Proposition):
    def __init__(self, *args):
        if len(args) != 2:
            raise TypeError('Expected exactly two args')

        self.lhs = unwrap_LTD_arg(args[0])
        self.rhs = unwrap_LTD_arg(args[1])


    def eval(self, step: DextStepIter) -> bool:
        pass

    def __str__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.lhs, self.rhs)
