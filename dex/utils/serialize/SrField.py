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
"""JSON-serializable field."""


class SrField(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 name,
                 type_,
                 dict_of=False,
                 list_of=False,
                 required_in_init=True,
                 default_value=None,
                 can_be_none=False,
                 possible_values=None):
        assert not (dict_of
                    and list_of), '{} cannot be dict and list!'.format(name)

        self.name = name
        self.type = type_
        self.dict_of = dict_of
        self.list_of = list_of
        self.required_in_init = required_in_init
        self.default_value = default_value
        self.can_be_none = can_be_none
        self.possible_values = possible_values

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name
