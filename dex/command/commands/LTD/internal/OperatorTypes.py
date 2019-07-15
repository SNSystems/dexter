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
    Composite, Proposition, Boolean, unwrap_LTD_arg
)

class UnaryOperator(Proposition):
    def __init__(self, *args):
        if len(args) != 1:
            raise TypeError('{} expected exactly one arg'.format(
                self.__class__.__name__))
        self.operand = unwrap_LTD_arg(args[0])

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.operand)

    def __repr__(self):
        return self.__str__()


class BinaryOperator(Proposition):
    def __init__(self, *args):
        if len(args) != 2:
            raise TypeError('{} expected exactly two args'.format(
                self.__class__.__name__))
        self.lhs = unwrap_LTD_arg(args[0])
        self.rhs = unwrap_LTD_arg(args[1])

    def __str__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.lhs, self.rhs)

    def __repr__(self):
        return self.__str__()


class BinaryOperatorTree(Composite, Proposition):
    """Build an expression tree starting with the rightmost operand.
    For example Fn(a, b, c) will build:
            op
            /\
            a  op
                /\
                b  c
    define op by implementing proposition_template.
    """
    def __init__(self, *args):
        if len(args) < 2:
            raise TypeError('{} expected at least 2 args'.format(
                self.__class__.__name__))

        # Keep args for printing
        self.args = args

        # Build a tree of binary expressions starting with the deepest rhs leaf.
        rhs = unwrap_LTD_arg(args[-1])
        i = len(args) - 2
        while i >= 0:
            lhs = unwrap_LTD_arg(args[i])
            rhs = self.__class__.proposition_template(lhs, rhs)
            i -= 1

        self.set_proposition(rhs)

    @abc.abstractmethod
    def proposition_template(p: Proposition, q: Proposition) -> Proposition:
        pass

    def __str__(self):
        return "{}{}".format(self.__class__.__name__, self.args)

    def __repr__(self):
        return self.__str__()
