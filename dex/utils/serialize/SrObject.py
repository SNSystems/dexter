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
"""JSON-serializable object."""

import abc
from collections import OrderedDict
import json
import unittest

from dex.utils import create_named_enum
from dex.utils.Exceptions import SrInitError
from dex.utils.serialize import SrField


def _serialize(value):
    if isinstance(value, list):
        value = [_serialize(v) for v in value]
    elif isinstance(value, dict):
        value = OrderedDict((v, _serialize(value[v])) for v in value)
    elif isinstance(value, SrObject):
        return value.to_serializable
    return value


def _unserialize(value, type_):
    try:
        return type_(sr_data=value)
    except (TypeError, KeyError):
        if isinstance(value, list):
            return [_unserialize(v, type_) for v in value]
        if isinstance(value, dict):
            return OrderedDict(
                (v, _unserialize(value[v], type_)) for v in value)
        return value


class SrObject(object, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def sr_fields(self):
        pass

    def _set_field(self, field, val):
        if field.possible_values is not None:
            if val and val not in field.possible_values:
                raise SrInitError(
                    'field "{}" value "{}" is not a valid value {}'.format(
                        field.name, val, field.possible_values))
        setattr(self, field.name, val)

    def _validate(self):  # noqa # pylint: disable=too-many-branches
        fields = self.sr_fields

        for field in fields:
            try:
                value = getattr(self, field.name)
            except KeyError:
                raise SrInitError('field "{}" has not been set.'.format(
                    field.name))

            if value is None:
                if not field.can_be_none:
                    raise SrInitError('field "{}" cannot be None'.format(
                        field.name))

            elif field.list_of:
                if not isinstance(value, list):
                    raise SrInitError('field "{}" is not a list ({})'.format(
                        field.name, value))

                for i, v in enumerate(value):
                    if not isinstance(v, field.type):
                        raise SrInitError(
                            'field "{}[{}]" is not type "{}" ({})'.format(
                                field.name, i, field.type, v))

            elif field.dict_of:
                if not isinstance(value, dict):
                    raise SrInitError('field "{}" is not a dict ({})'.format(
                        field.name, value))

                for v in value:
                    if not isinstance(value[v], field.type):
                        raise SrInitError(
                            'field "{}[{}]" is not type "{}" ({})'.format(
                                field.name, v, field.type, value[v]))

            else:
                if not isinstance(value, field.type):
                    raise SrInitError(
                        'field "{}" should be type "{}" but is type "{}" ({})'.
                        format(field.name, field.type, type(value), value))

    def __init__(self, **kwargs):

        fields = self.sr_fields

        # Validate that the sr_fields property contains a list of SrFields.
        assert isinstance(fields, list), type(fields)
        for field in fields:
            assert isinstance(field, SrField), (field, type(field))

        # Try to load from serialized data, otherwise initialize from the
        # kwargs.
        if not self._load_sr_data(kwargs):
            for field in fields:
                if field.required_in_init:
                    value = kwargs.pop(field.name)
                else:
                    default_value = field.default_value
                    if isinstance(field.default_value, type):
                        default_value = default_value()
                    value = kwargs.pop(field.name, default_value)

                self._set_field(field, value)

        # At this point all kwargs should have been popped.
        if kwargs:
            raise SrInitError('unexpected args: {}'.format(kwargs))

        self._validate()

    def _load_sr_data(self, kwargs):
        if 'sr_data' not in kwargs:
            return False

        sr_data = kwargs.pop('sr_data')

        if kwargs:
            raise SrInitError('unexpected args: {}'.format(kwargs))

        if not isinstance(sr_data, dict):
            raise TypeError(sr_data)

        sr_data = sr_data.copy()

        for field in self.sr_fields:
            value = sr_data.pop(field.name)
            value = _unserialize(value, field.type)
            self._set_field(field, value)

        if sr_data:
            raise SrInitError(
                'unexpected serialized data "{}"'.format(sr_data))

        return True

    @property
    def to_serializable(self):
        data = []
        for field in self.sr_fields:
            value = getattr(self, field.name)
            data.append((field.name, _serialize(value)))

        data = OrderedDict(data)

        keys = sorted([str(k) for k in data.keys()])
        expected_keys = sorted([k.name for k in self.sr_fields])
        assert keys == expected_keys, (keys, expected_keys)

        for key in data:
            # We don't allow unordered types (e.g. dicts) here.
            # All aggregate types must be ordered.
            assert isinstance(data[key],
                              (list, OrderedDict, str, bool, int,
                               type(None))), (key, data[key], type(data[key]))

        return data

    @property
    def as_json(self):
        return json.dumps(self.to_serializable, indent=2)

    def __eq__(self, other):
        return all(
            getattr(self, field.name) == getattr(other, field.name)
            for field in self.sr_fields)

    def __hash__(self):
        return hash((getattr(self, field.name)) for field in self.sr_fields)


# pylint: disable=no-member
class TestSrObject(unittest.TestCase):
    class TestObject1(SrObject):
        @property
        def sr_fields(self):
            return [
                SrField('aa', str),
                SrField('bb', int),
            ]

    class TestObject2(SrObject):
        @property
        def sr_fields(self):
            return [
                SrField('cc', str),
                SrField('dd', int, list_of=True),
            ]

    class TestObject3(SrObject):
        @property
        def sr_fields(self):
            return [
                SrField('ee', str),
                SrField('ff', int, dict_of=True, can_be_none=True),
            ]

    class TestObject4(SrObject):
        @property
        def sr_fields(self):
            return [
                SrField('gg', TestSrObject.TestObject1),
            ]

    class TestObject5(SrObject):
        @property
        def sr_fields(self):
            return [
                SrField('hh', TestSrObject.TestObject1, list_of=True),
                SrField('ii', TestSrObject.TestObject4, dict_of=True),
            ]

    def test_init_validation(self):

        # valid
        TestSrObject.TestObject1(aa='41', bb=42)  # noqa

        # missing args
        with self.assertRaises(KeyError):
            TestSrObject.TestObject1()  # noqa

        with self.assertRaises(KeyError):
            TestSrObject.TestObject1(aa='41')  # noqa

        # unexpected args
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject1(aa='41', bb=42, cc=43)  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject1(aa='41', bb=42, sr_data={})  # noqa

        # aa is not a string
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject1(aa=41, bb=42)  # noqa

        # valid
        TestSrObject.TestObject2(cc='41', dd=[42, 43])  # noqa

        # dd is not a list
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(cc='41', dd=42)  # noqa

        # bb is not a list of ints
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(cc='41', dd=['42', '43'])  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(cc='41', dd=[42, '43'])  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(cc='41', dd={42: '43'})  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(cc='41', dd={42: 43})  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject2(
                cc='41', dd=OrderedDict(((42, 43), )))  # noqa

        # valid
        TestSrObject.TestObject3(ee='41', ff={42: 43})  # noqa
        TestSrObject.TestObject3(ee='41', ff=OrderedDict(((42, 43), )))  # noqa
        TestSrObject.TestObject3(ee='41', ff=None)  # noqa

        # ee cannot be none
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject3(ee=None, ff=None)  # noqa

        # ff is not a dict
        with self.assertRaises(SrInitError):
            TestSrObject.TestObject3(ee='41', ff=42)  # noqa

        with self.assertRaises(SrInitError):
            TestSrObject.TestObject3(ee='41', ff=[42, 43])  # noqa

        # valid
        t1 = TestSrObject.TestObject1(aa='41', bb=42)
        t4 = TestSrObject.TestObject4(gg=t1)
        TestSrObject.TestObject5(hh=[t1], ii={'jj': t4})

    def test_serialize(self):  # pylint: disable=too-many-statements
        t1 = TestSrObject.TestObject1(aa='41', bb=42)
        self.assertEqual(t1.aa, '41')
        self.assertEqual(t1.bb, 42)
        s1 = t1.to_serializable
        self.assertEqual(t1.aa, s1['aa'])
        self.assertEqual(t1.bb, s1['bb'])

        t2 = TestSrObject.TestObject2(cc='41', dd=[42, 43])
        self.assertEqual(t2.cc, '41')
        self.assertEqual(t2.dd, [42, 43])
        s2 = t2.to_serializable
        self.assertEqual(t2.cc, s2['cc'])
        self.assertEqual(t2.dd, s2['dd'])

        t3a = TestSrObject.TestObject3(ee='41', ff={42: 43})
        self.assertEqual(t3a.ee, '41')
        self.assertEqual(t3a.ff, {42: 43})
        s3a = t3a.to_serializable
        self.assertEqual(t3a.ee, s3a['ee'])
        self.assertEqual(t3a.ff, s3a['ff'])
        self.assertEqual(s3a['ff'][42], 43)
        with self.assertRaises(KeyError):
            _ = s3a['ff'][43]  # noqa

        t3b = TestSrObject.TestObject3(ee='41', ff=OrderedDict(((42, 43), )))
        self.assertEqual(t3b.ee, '41')
        self.assertEqual(t3b.ff, {42: 43})
        s3b = t3b.to_serializable
        self.assertEqual(t3b.ee, s3b['ee'])
        self.assertEqual(t3b.ff, s3b['ff'])
        self.assertEqual(s3b['ff'][42], 43)
        with self.assertRaises(KeyError):
            _ = s3b['ff'][43]  # noqa

        t4 = TestSrObject.TestObject4(gg=t1)
        self.assertEqual(t4.gg.aa, t1.aa)
        self.assertEqual(t4.gg.bb, t1.bb)
        s4 = t4.to_serializable
        self.assertEqual(s4['gg']['aa'], t1.aa)
        self.assertEqual(s4['gg']['bb'], t1.bb)

        t5 = TestSrObject.TestObject5(hh=[t1], ii={'jj': t4})
        self.assertEqual(len(t5.hh), 1)
        self.assertEqual(t5.hh[0].aa, t1.aa)
        self.assertEqual(t5.hh[0].bb, t1.bb)
        self.assertEqual(len(t5.ii), 1)
        self.assertEqual(t5.ii['jj'].gg.aa, t4.gg.aa)
        self.assertEqual(t5.ii['jj'].gg.bb, t4.gg.bb)
        s5 = t5.to_serializable

        self.assertEqual(len(s5['hh']), 1)
        self.assertEqual(s5['hh'][0]['aa'], t1.aa)
        self.assertEqual(s5['hh'][0]['bb'], t1.bb)
        self.assertEqual(len(s5['ii']), 1)
        self.assertEqual(s5['ii']['jj']['gg']['aa'], t4.gg.aa)
        self.assertEqual(s5['ii']['jj']['gg']['bb'], t4.gg.bb)

    def test_reserialize(self):
        t1 = TestSrObject.TestObject1(aa='41', bb=42)
        r1 = TestSrObject.TestObject1(sr_data=json.loads(t1.as_json))
        self.assertDictEqual(t1.to_serializable, r1.to_serializable)
        self.assertEqual(t1.as_json, r1.as_json)
        self.assertEqual(r1.aa, '41')
        self.assertEqual(r1.bb, 42)

        t2 = TestSrObject.TestObject2(cc='41', dd=[42, 43])
        r2 = TestSrObject.TestObject2(sr_data=json.loads(t2.as_json))
        self.assertDictEqual(t2.to_serializable, r2.to_serializable)
        self.assertEqual(t2.as_json, r2.as_json)
        self.assertEqual(r2.cc, '41')
        self.assertEqual(r2.dd, [42, 43])

        t3a = TestSrObject.TestObject3(ee='41', ff={'42': 43})
        r3a = TestSrObject.TestObject3(sr_data=json.loads(t3a.as_json))
        self.assertDictEqual(t3a.to_serializable, r3a.to_serializable)
        self.assertEqual(t3a.as_json, r3a.as_json)
        self.assertEqual(r3a.ee, '41')
        self.assertEqual(r3a.ff, {'42': 43})

        t3b = TestSrObject.TestObject3(ee='41', ff=OrderedDict((('42', 43), )))
        r3b = TestSrObject.TestObject3(sr_data=json.loads(t3b.as_json))
        self.assertDictEqual(t3b.to_serializable, r3b.to_serializable)
        self.assertEqual(t3b.as_json, r3b.as_json)
        self.assertEqual(r3b.ee, '41')
        self.assertEqual(r3b.ff, {'42': 43})

        t4 = TestSrObject.TestObject4(gg=t1)
        r4 = TestSrObject.TestObject4(sr_data=json.loads(t4.as_json))
        self.assertDictEqual(t4.to_serializable, r4.to_serializable)
        self.assertEqual(t4.as_json, r4.as_json)
        self.assertEqual(r4.gg.aa, t1.aa)
        self.assertEqual(r4.gg.bb, t1.bb)

        t5 = TestSrObject.TestObject5(hh=[t1], ii={'jj': t4})
        r5 = TestSrObject.TestObject5(sr_data=json.loads(t5.as_json))
        q5 = TestSrObject.TestObject5(sr_data=json.loads(r5.as_json))
        self.assertDictEqual(t5.to_serializable, r5.to_serializable)
        self.assertEqual(t5.as_json, r5.as_json)
        self.assertDictEqual(t5.to_serializable, q5.to_serializable)
        self.assertEqual(t5.as_json, q5.as_json)

        self.assertEqual(len(r5.hh), 1)
        self.assertEqual(r5.hh[0].aa, t1.aa)
        self.assertEqual(r5.hh[0].bb, t1.bb)
        self.assertEqual(len(r5.ii), 1)
        self.assertEqual(r5.ii['jj'].gg.aa, t4.gg.aa)
        self.assertEqual(r5.ii['jj'].gg.bb, t4.gg.bb)

    def test_serialize_enum(self):
        e = create_named_enum('FOO', 'BAR', 'BAZ')

        class TestObject(SrObject):
            sr_fields = [
                SrField(
                    'kk',
                    str,
                    possible_values=e.possible_values,
                    can_be_none=True),
                SrField('ll', str, possible_values=e.possible_values)
            ]

        t = TestObject(kk=e.FOO, ll=e.BAR)
        self.assertEqual(t.kk, e.FOO)
        self.assertEqual(t.ll, e.BAR)
        r = TestObject(sr_data=json.loads(t.as_json))
        self.assertEqual(r.kk, e.FOO)
        self.assertEqual(r.ll, e.BAR)
        s = TestObject(sr_data=json.loads(r.as_json))
        self.assertEqual(s.kk, e.FOO)
        self.assertEqual(s.ll, e.BAR)

        self.assertEqual(t.as_json, r.as_json)
        self.assertEqual(t.as_json, s.as_json)

        t = TestObject(kk=None, ll=e.BAZ)
        self.assertEqual(t.kk, None)
        self.assertEqual(t.ll, e.BAZ)
        r = TestObject(sr_data=json.loads(t.as_json))
        self.assertEqual(r.kk, None)
        self.assertEqual(r.ll, e.BAZ)
        s = TestObject(sr_data=json.loads(r.as_json))
        self.assertEqual(s.kk, None)
        self.assertEqual(s.ll, e.BAZ)

        # ll cannot be None
        with self.assertRaises(SrInitError):
            TestObject(kk=None, ll=None)  # noqa

        TestObject(kk=None, ll='BAZ')

        # invalid value
        with self.assertRaises(SrInitError):
            TestObject(kk=None, ll='WIBBLE')

    def test_default_value(self):
        class TestObject1(SrObject):
            sr_fields = [SrField('mm', int, required_in_init=False)]

        # mm default is None but cannot be None.
        with self.assertRaises(SrInitError):
            TestObject1()  # noqa
        t1 = TestObject1(mm=3)
        self.assertEqual(t1.mm, 3)

        class TestObject2(SrObject):
            sr_fields = [
                SrField('nn', int, required_in_init=False, default_value='x')
            ]

        # nn default is string but must be int.
        with self.assertRaises(SrInitError):
            TestObject2()  # noqa
        t2 = TestObject2(nn=4)
        self.assertEqual(t2.nn, 4)

        class TestObject3(SrObject):
            sr_fields = [
                SrField(
                    'oo',
                    int,
                    required_in_init=False,
                    dict_of=True,
                    default_value=OrderedDict)
            ]

        t3 = TestObject3()
        self.assertEqual(t3.oo, {})
