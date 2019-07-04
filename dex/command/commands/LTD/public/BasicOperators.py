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
        print("v--- Not ---v")
        result =  not self.operand.eval(trace_iter)
        print("^--- Not (ret {}) ---^".format(result))
        return result

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__str__()


class And(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        print("v--- And ---v")
        result = (self.lhs.eval(trace_iter)
                and self.rhs.eval(trace_iter))
        print("^--- And (ret {}) ---^".format(result))
        return result


    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__str__()


class Or(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        return (self.lhs.eval(trace_iter)
                or self.rhs.eval(trace_iter))

    def __str__(self):
        return super().__str__()

def __repr__(self):
        return super().__str__()


class Weak(BinaryOperator):
    """ Weak(p, q) == p must hold until q and q may never hold
    """
    def __init__(self, *args):
        super().__init__(*args)

    def eval(self, trace_iter: DextStepIter):
        print("v--- {} ---v".format(self))
        trace_iter = copy(trace_iter)
        while not trace_iter.at_end():
            print("v--- Weak step ---v")
            result = self.rhs.eval(trace_iter)
            print("Weak rhs -- {}".format(result))
            if result is True:
                print("^--- Weak step (rhs True) ---^")
                return True
            else:
                result = self.lhs.eval(trace_iter)
                print("Weak lhs -- {}".format(result))
                if result is False:
                    print("^--- Weak step (lhs False) ---^")
                    return False
            print("^--- Weak step ---^")
            trace_iter.increment()

        print("^--- Weak (ret False)---^")
        return True

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__str__()


class Until(BinaryOperator):
    def __init__(self, *args):
        super().__init__(*args)

## @@ consider renaming to reduce confusion with CommandBase
    def eval(self, trace_iter: DextStepIter):
        print("v--- {} ---v".format(self))
        trace_iter = copy(trace_iter)
        while not trace_iter.at_end():
            print("v--- Until step ---v")
            result = self.rhs.eval(trace_iter)
            print("Until rhs -- {}".format(result))
            if result is True:
                print("^--- Until step (rhs {})---^".format(result))
                return True
            else:
                result = self.lhs.eval(trace_iter)
                print("Until lhs -- {}".format(result))
                if result is False:
                    print("^--- Until step (lhs False)---^")
                    return False
            print("^--- Until step ---^")
            trace_iter.increment()

        print("^--- Until (ret False)---^")
        return False

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__str__()
