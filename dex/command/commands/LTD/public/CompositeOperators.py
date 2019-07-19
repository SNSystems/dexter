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
"""LTD operators which are completely defined in terms of other LTD operators.
"""

from dex.dextIR import DextStepIter, StepIR
from dex.command.commands.LTD.internal.Proposition import Proposition, Composite
from dex.command.commands.LTD.internal.OperatorTypes import (
    BinaryOperator, UnaryOperator, BinaryOperatorTree
)
from dex.command.commands.LTD.public.BasicOperators import (
    And, Or, Not, Until, Weak, Next,
)


class Eventually(Composite, UnaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.set_proposition(Until(True, self.operand))


class Release(Composite, BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.set_proposition(Weak(self.rhs, And(self.rhs, self.lhs)))


class Henceforth(Composite, UnaryOperator):
    def __init__(self, *args):
        super().__init__(*args)
        self.set_proposition(Weak(self.operand, False))


class After(Composite, BinaryOperator):
    """After(p, q): q must hold. Any time after that p must hold. p and q may
    not hold simultaneously.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.set_proposition(And(self.rhs, Next(Eventually(self.lhs))))


class Ordered(BinaryOperatorTree):
    def proposition_template(p: Proposition, q: Proposition):
        return After(q, p)
