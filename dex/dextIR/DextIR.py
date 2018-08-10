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
"""Root for dextIR serialization types."""

from collections import OrderedDict
import json
import os
import unittest

from dex.dextIR.CommandIR import CommandIR
from dex.dextIR.CommandListIR import CommandListIR
from dex.dextIR.DebuggerIR import DebuggerIR
from dex.dextIR.FrameIR import FrameIR
from dex.dextIR.LocIR import LocIR
from dex.dextIR.StepIR import StepIR, StepKind, StopReason
from dex.dextIR.ValueIR import ValueIR
from dex.utils.compatibility import assertRaisesRegex, string_types
from dex.utils.Exceptions import ImportDextIRException, SrInitError
from dex.utils.serialize import SrField, SrObject


def importDextIR(json_string):
    try:
        return DextIR(
            sr_data=json.loads(json_string, object_pairs_hook=OrderedDict))
    except KeyError as e:
        raise ImportDextIRException('missing key: <r>{}</>'.format(e))
    except (SrInitError, ValueError) as e:
        raise ImportDextIRException(e)


def _step_kind_func(context, step):
    if step.current_location.path in context.options.source_files:
        return StepKind.FUNC

    if step.current_location.path is None:
        return StepKind.FUNC_UNKNOWN

    return StepKind.FUNC_EXTERNAL


# pylint: disable=no-member
class DextIR(SrObject):
    sr_fields = [
        SrField('dexter_version', string_types),
        SrField('executable_path', string_types),
        SrField('source_paths', string_types, list_of=True),
        SrField(
            'builder', DebuggerIR, can_be_none=True, required_in_init=False),
        SrField(
            'debugger', DebuggerIR, can_be_none=True, required_in_init=False),
        SrField(
            'steps',
            StepIR,
            list_of=True,
            required_in_init=False,
            default_value=list),
        SrField(
            'commands',
            CommandListIR,
            dict_of=True,
            required_in_init=False,
            default_value=OrderedDict)
    ]

    def __str__(self):
        colors = 'rgby'
        st = '## BEGIN ##\n'
        color_idx = 0
        for step in self.steps:
            if step.step_kind in (StepKind.FUNC, StepKind.FUNC_EXTERNAL,
                                  StepKind.FUNC_UNKNOWN):
                color_idx += 1

            color = colors[color_idx % len(colors)]
            st += '<{}>{}</>\n'.format(color, step)
        st += '## END ({} step{}) ##\n'.format(
            self.num_steps, '' if self.num_steps == 1 else 's')
        return st

    @property
    def num_steps(self):
        return len(self.steps)

    def new_step(self, context, step):
        assert isinstance(step, StepIR), type(step)
        if step.current_function is None:
            step.step_kind = StepKind.UNKNOWN
        else:
            try:
                prev_step = self.steps[-1]
            except IndexError:
                step.step_kind = _step_kind_func(context, step)
            else:
                if prev_step.current_function is None:
                    step.step_kind = StepKind.UNKNOWN
                elif prev_step.current_function != step.current_function:
                    step.step_kind = _step_kind_func(context, step)
                elif prev_step.current_location == step.current_location:
                    step.step_kind = StepKind.SAME
                elif prev_step.current_location > step.current_location:
                    step.step_kind = StepKind.BACKWARD
                elif prev_step.current_location < step.current_location:
                    step.step_kind = StepKind.FORWARD

        self.steps.append(step)
        return step

    def clear_steps(self):
        setattr(self, 'steps', list())


class TestDextIR(unittest.TestCase):
    def test_json(self):
        # Initialize a new DextIR and populate it with some data.

        class context(object):
            class options(object):
                source_files = []

        debugger = DebuggerIR(name='MockDebugger', version='1.0')

        commands = {'DexWatch': CommandListIR()}
        commands['DexWatch'].append(
            CommandIR(
                loc=LocIR(path='foo/bar', lineno=1, column=None),
                raw_text="DexWatch('a')"))
        commands['DexWatch'].append(
            CommandIR(
                loc=LocIR(path='foo/baz', lineno=75, column=None),
                raw_text='DexWatch("b", "c")'))

        sc = DextIR(
            dexter_version='',
            debugger=debugger,
            commands=commands,
            executable_path='',
            source_paths=[])
        frames = [
            FrameIR(
                function='main',
                is_inlined=False,
                loc=LocIR(path='smain.c', lineno=12, column=4))
        ]
        step = sc.new_step(
            context,
            StepIR(
                step_index=0, frames=frames[:], stop_reason=StopReason.STEP))
        step.watches['xx'] = ValueIR(
            expression='xx',
            value='2',
            type='int',
            error_string=None,
            could_evaluate=True,
            is_optimized_away=False,
            is_irretrievable=False)
        frames.insert(
            0,
            FrameIR(
                function='bar',
                is_inlined=True,
                loc=LocIR(path='sbar.c', lineno=12, column=3)))

        step = sc.new_step(
            context,
            StepIR(
                step_index=1, frames=frames[:], stop_reason=StopReason.STEP))
        step.watches['yy'] = ValueIR(
            expression='yy',
            value='hello world',
            type='std::string const&',
            error_string=None,
            could_evaluate=True,
            is_optimized_away=False,
            is_irretrievable=False)
        frames.insert(
            0,
            FrameIR(
                function='foo',
                is_inlined=True,
                loc=LocIR(path='sfoo.c', lineno=10, column=1)))
        step = sc.new_step(
            context,
            StepIR(
                step_index=2, frames=frames[:], stop_reason=StopReason.STEP))
        step.watches['yy'] = ValueIR(
            expression='yy',
            value='hello cruel world',
            type='std::string const&',
            error_string=None,
            could_evaluate=True,
            is_optimized_away=False,
            is_irretrievable=False)
        step.watches['zz'] = ValueIR(
            expression=None,
            value=None,
            type=None,
            error_string=None,
            could_evaluate=False,
            is_optimized_away=False,
            is_irretrievable=False)

        # Write the DextIR out as json.
        sc_json = sc.as_json

        # Create a new DextIR and populate it with the json data.
        sc2 = importDextIR(json_string=sc_json)
        sc3 = importDextIR(json_string=sc2.as_json)

        self.assertEqual(sc_json, sc2.as_json)
        self.assertEqual(sc_json, sc3.as_json)

        self.assertEqual(sc2.debugger.name, 'MockDebugger')
        self.assertEqual(sc2.commands['DexWatch'][0].loc.path,
                         os.path.join('foo', 'bar'))
        self.assertEqual(sc2.commands['DexWatch'][0].loc.lineno, 1)
        self.assertEqual(sc2.commands['DexWatch'][0].raw_text, "DexWatch('a')")
        self.assertEqual(sc2.commands['DexWatch'][1].loc.path,
                         os.path.join('foo', 'baz'))
        self.assertEqual(sc2.commands['DexWatch'][1].loc.lineno, 75)
        self.assertEqual(sc2.commands['DexWatch'][1].raw_text,
                         'DexWatch("b", "c")')

        # Check that we really do have the data in our new DextIR.
        self.assertEqual(sc2.num_steps, 3)
        self.assertEqual(sc2.steps[0].current_function, 'main')
        self.assertEqual(sc2.steps[0].num_frames, 1)
        self.assertFalse(sc2.steps[0].current_frame.is_inlined)

        self.assertEqual(
            sc2.steps[0].watches['xx'],
            ValueIR(
                expression='xx',
                value='2',
                type='int',
                error_string=None,
                could_evaluate=True,
                is_optimized_away=False,
                is_irretrievable=False))

        self.assertEqual(sc2.steps[1].current_function, 'bar')
        self.assertEqual(sc2.steps[1].num_frames, 2)
        self.assertTrue(sc2.steps[1].current_frame.is_inlined)

        with self.assertRaises(KeyError):
            _ = sc2.steps[1].watches['xx']  # noqa

        self.assertEqual(
            sc2.steps[1].watches['yy'],
            ValueIR(
                expression='yy',
                value='hello world',
                type='std::string const&',
                error_string=None,
                could_evaluate=True,
                is_optimized_away=False,
                is_irretrievable=False))

        self.assertEqual(sc2.steps[2].current_function, 'foo')
        self.assertEqual(sc2.steps[2].num_frames, 3)
        self.assertTrue(sc2.steps[2].current_frame.is_inlined)

        self.assertEqual(
            sc2.steps[2].watches['yy'],
            ValueIR(
                expression='yy',
                value='hello cruel world',
                type='std::string const&',
                error_string=None,
                could_evaluate=True,
                is_optimized_away=False,
                is_irretrievable=False))

        self.assertEqual(
            sc2.steps[2].watches['zz'],
            ValueIR(
                expression=None,
                value=None,
                type=None,
                error_string=None,
                could_evaluate=False,
                is_optimized_away=False,
                is_irretrievable=False))

        self.assertEqual(sc2.steps[2].frames[0].loc,
                         LocIR(path='sfoo.c', lineno=10, column=1))
        self.assertEqual(sc2.steps[2].frames[1].loc,
                         LocIR(path='sbar.c', lineno=12, column=3))
        self.assertEqual(sc2.steps[2].frames[2].loc,
                         LocIR(path='smain.c', lineno=12, column=4))

    def test_valid_json(self):
        with self.assertRaises(ImportDextIRException):
            importDextIR('test')

        with self.assertRaises(ImportDextIRException):
            importDextIR('{ }')

        with assertRaisesRegex(self, ImportDextIRException,
                               'unexpected serialized data '):
            importDextIR('''{
        "dexter_version": "",
        "executable_path": "",
        "source_paths": [],
        "builder": null,
        "debugger": null,
        "steps": [],
        "commands": {},
        "test": [] }''')

        with assertRaisesRegex(self, ImportDextIRException,
                               'field "steps" cannot be None'):
            importDextIR('''{
        "dexter_version": "",
        "executable_path": "",
        "source_paths": [],
        "builder": null,
        "debugger": null,
        "steps" : null,
        "commands": {} }''')

        with assertRaisesRegex(self, ImportDextIRException,
                               'field "steps" is not a list'):
            importDextIR('''{
        "dexter_version": "",
        "executable_path": "",
        "source_paths": [],
        "builder": null,
        "debugger": null,
        "steps" : { },
        "commands": { } }''')

        importDextIR('''{
         "dexter_version": "",
         "executable_path": "",
         "source_paths": [],
         "builder": null,
         "debugger": null,
          "commands": {
            "DexWatch": {
              "command_list": [
                {
                  "loc" : {
                    "path": "foo/bar",
                    "lineno": 1,
                    "column": null
                    },
                  "raw_text": "DexWatch('a')"
                  }
                ]
              }
            },
            "steps": [
            {
              "step_index": 0,
              "step_kind": null,
              "stop_reason": "BREAKPOINT",
              "frames": [
                {
                  "function": null,
                  "is_inlined": false,
                  "loc": {
                    "path": null,
                    "lineno": null,
                    "column": null
                  }
                }
              ],
              "watches": { }
            }
          ]
        }''')

        with self.assertRaises(ImportDextIRException):
            importDextIR('''{
        "dexter_version": "",
        "executable_path": "",
        "source_paths": [],
        "builder": null,
        "debugger": null,
        "commands": { },
        "steps" : [null] }''')
