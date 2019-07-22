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
from dex.command.CommandBase import CommandBase
from dex.command.commands.LTD.internal.Proposition import Boolean
from dex.dextIR import DextIR, DextStepIter
from dex.command.commands.LTD import (
    Or, And, Not, Next, Weak, After, Until, Expect, Release, Eventually,
    Henceforth, ExpectState, Ordered
)


class DexVerify(CommandBase):
    """Define an LTD model which expresses expected debugging behaviour.

    DexVerify(proposition)

    See Commands.md for more info.
    """

    def __init__(self, *args):
        if len(args) != 1:
            raise TypeError('Expected exactly one arg')

        self.model = args[0]
        if isinstance(self.model, bool):
            self.model = Boolean(self.model)

    def eval(self, program: DextIR) -> bool:
        # [TODO] return (bool, list) where list is a set of nested lists of
        # string which describte the verification trace
        trace_iter = DextStepIter(program)
        return self.model.eval(trace_iter)

    def get_subcommands():
        # LTD operators which are exposed to test writers through DexVerify.
        return {
            'Or': Or,
            'And': And,
            'Not': Not,
            'Next': Next,
            'Weak': Weak,
            'After': After,
            'Until': Until,
            'Expect': Expect,
            'Ordered': Ordered,
            'Release': Release,
            'Eventually': Eventually,
            'Henceforth': Henceforth,
            'ExpectState': ExpectState,
        }

    def __str__(self):
        return "DexVerify({})".format(self.model)

    def __repr__(self):
        return self.__str__()
