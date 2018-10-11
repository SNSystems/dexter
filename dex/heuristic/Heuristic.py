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
"""Calculate a 'score' based on some dextIR.
Assign penalties based on different commands to decrease the score.
1.000 would be a perfect score.
0.000 is the worst theoretical score possible.
"""

from collections import defaultdict, namedtuple
import os

from dex.command import get_command_object

PenaltyCommand = namedtuple('PenaltyCommand', ['pen_dict', 'max_penalty'])
# 'meta' field used in different ways by different things
PenaltyInstance = namedtuple('PenaltyInstance', ['meta', 'the_penalty'])


class StepValueInfo(object):
    def __init__(self, step_index, value_info):
        self.step_index = step_index
        self.value_info = value_info

    def __str__(self):
        return '{}:{}'.format(self.step_index, self.value_info)

    def __eq__(self, other):
        return (self.value_info.expression == other.value_info.expression
                and self.value_info.value == other.value_info.value)

    def __hash__(self):
        return hash(self.value_info.expression, self.value_info.value)


def add_heuristic_tool_arguments(parser):
    parser.add_argument(
        '--penalty-variable-optimized',
        type=int,
        default=3,
        help='set the penalty multiplier for each'
        ' occurrence of a variable that was optimized'
        ' away',
        metavar='<int>')
    parser.add_argument(
        '--penalty-misordered-values',
        type=int,
        default=3,
        help='set the penalty multiplier for each'
        ' occurrence of a misordered value.',
        metavar='<int>')
    parser.add_argument(
        '--penalty-irretrievable',
        type=int,
        default=4,
        help='set the penalty multiplier for each'
        " occurrence of a variable that couldn't"
        ' be retrieved',
        metavar='<int>')
    parser.add_argument(
        '--penalty-not-evaluatable',
        type=int,
        default=5,
        help='set the penalty multiplier for each'
        " occurrence of a variable that couldn't"
        ' be evaluated',
        metavar='<int>')
    parser.add_argument(
        '--penalty-missing-values',
        type=int,
        default=6,
        help='set the penalty multiplier for each missing'
        ' value',
        metavar='<int>')
    parser.add_argument(
        '--penalty-incorrect-values',
        type=int,
        default=7,
        help='set the penalty multiplier for each'
        ' occurrence of an unexpected value.',
        metavar='<int>')


class Heuristic(object):
    def __init__(self, context, steps):
        self.context = context
        self.penalties = {}

        worst_penalty = max([
            self.penalty_variable_optimized, self.penalty_irretrievable,
            self.penalty_not_evaluatable, self.penalty_incorrect_values,
            self.penalty_missing_values
        ])

        # Get DexExpectWatchValue results.
        try:
            for watch in getattr(
                    steps, 'commands')['DexExpectWatchValue'].command_list:
                command = get_command_object(watch)
                command(steps)
                maximum_possible_penalty = min(3, len(
                    command.values)) * worst_penalty
                name, p = self._calculate_expect_watch_penalties(
                    command, maximum_possible_penalty)
                self.penalties[name] = PenaltyCommand(p,
                                                      maximum_possible_penalty)
        except KeyError:
            pass

        # Get the total number of each step kind.
        step_kind_counts = defaultdict(int)
        for step in getattr(steps, 'steps'):
            step_kind_counts[step.step_kind] += 1

        # Get DexExpectStepKind results.
        penalties = defaultdict(list)
        maximum_possible_penalty_all = 0
        try:
            for step_kind in getattr(
                    steps, 'commands')['DexExpectStepKind'].command_list:
                command = get_command_object(step_kind)
                command()
                # Cap the penalty at 2 * expected count or else 1
                maximum_possible_penalty = max(command.count * 2, 1)
                penalty = abs(command.count - step_kind_counts[command.name])
                actual_penalty = min(penalty, maximum_possible_penalty)
                key = (command.name
                       if actual_penalty else '<g>{}</>'.format(command.name))
                penalties[key] = [PenaltyInstance(penalty, actual_penalty)]
                maximum_possible_penalty_all += maximum_possible_penalty
            self.penalties['step kind differences'] = PenaltyCommand(
                penalties, maximum_possible_penalty_all)
        except KeyError:
            pass

    def _calculate_expect_watch_penalties(self, c, maximum_possible_penalty):
        penalties = defaultdict(list)

        if c.line_range[0] == c.line_range[-1]:
            line_range = str(c.line_range[0])
        else:
            line_range = '{}-{}'.format(c.line_range[0], c.line_range[-1])

        name = '{}:{} [{}]'.format(
            os.path.basename(c.path), line_range, c.expression)

        num_actual_watches = len(c.expected_watches) + len(
            c.unexpected_watches)

        penalty_available = maximum_possible_penalty

        # Only penalize for missing values if we have actually seen a watch
        # that's returned us an actual value at some point, or if we've not
        # encountered the value at all.
        if num_actual_watches or c.times_encountered == 0:
            for v in c.missing_values:
                current_penalty = min(penalty_available,
                                      self.penalty_missing_values)
                penalty_available -= current_penalty
                penalties['missing values'].append(
                    PenaltyInstance(v, current_penalty))

        for v in c.encountered_values:
            penalties['<g>expected encountered values</>'].append(
                PenaltyInstance(v, 0))

        penalty_descriptions = [
            (self.penalty_not_evaluatable, c.invalid_watches,
             'could not evaluate'),
            (self.penalty_variable_optimized, c.optimized_out_watches,
             'result optimized away'),
            (self.penalty_misordered_values, c.misordered_watches,
             'misordered result'),
            (self.penalty_irretrievable, c.irretrievable_watches,
             'result could not be retrieved'),
            (self.penalty_incorrect_values, c.unexpected_watches,
             'unexpected result'),
        ]

        for penalty_score, watches, description in penalty_descriptions:
            # We only penalize the encountered issue for each missing value per
            # command but we still want to record each one, so set the penalty
            # to 0 after the threshold is passed.
            times_to_penalize = len(c.missing_values)

            for w in watches:
                times_to_penalize -= 1
                penalty_score = min(penalty_available, penalty_score)
                penalty_available -= penalty_score
                penalties[description].append(
                    PenaltyInstance(w, penalty_score))
                if not times_to_penalize:
                    penalty_score = 0

        return name, penalties

    @property
    def penalty(self):
        result = 0

        maximum_allowed_penalty = 0
        for name in self.penalties:
            maximum_allowed_penalty += self.penalties[name].max_penalty
            value = self.penalties[name].pen_dict
            for category in value:
                result += sum(x.the_penalty for x in value[category])
        return min(result, maximum_allowed_penalty)

    @property
    def max_penalty(self):
        return sum(self.penalties[p].max_penalty for p in self.penalties)

    @property
    def score(self):
        try:
            return 1.0 - (self.penalty / float(self.max_penalty))
        except ZeroDivisionError:
            return float('nan')

    @property
    def summary_string(self):
        score = self.score
        isnan = score != score  # pylint: disable=comparison-with-itself
        color = 'g'
        if score < 0.25 or isnan:
            color = 'r'
        elif score < 0.75:
            color = 'y'

        return '<{}>({:.4f})</>'.format(color, score)

    @property
    def verbose_output(self):  # noqa
        string = ''
        string += ('\n')
        for command in sorted(self.penalties):
            maximum_possible_penalty = self.penalties[command].max_penalty
            total_penalty = 0
            lines = []
            for category in sorted(self.penalties[command].pen_dict):
                lines.append('    <r>{}</>:\n'.format(category))

                for result, penalty in self.penalties[command].pen_dict[
                        category]:
                    if isinstance(result, StepValueInfo):
                        text = 'step {}'.format(result.step_index)
                        if result.value_info.value:
                            text += ' ({})'.format(result.value_info.value)
                    else:
                        text = str(result)
                    if penalty:
                        assert penalty > 0, penalty
                        total_penalty += penalty
                        text += ' <r>[-{}]</>'.format(penalty)
                    lines.append('      {}\n'.format(text))

                lines.append('\n')

            string += ('  <b>{}</> <y>[{}/{}]</>\n'.format(
                command, total_penalty, maximum_possible_penalty))
            for line in lines:
                string += (line)
        string += ('\n')
        return string

    @property
    def penalty_variable_optimized(self):
        return self.context.options.penalty_variable_optimized

    @property
    def penalty_irretrievable(self):
        return self.context.options.penalty_irretrievable

    @property
    def penalty_not_evaluatable(self):
        return self.context.options.penalty_not_evaluatable

    @property
    def penalty_incorrect_values(self):
        return self.context.options.penalty_incorrect_values

    @property
    def penalty_missing_values(self):
        return self.context.options.penalty_missing_values

    @property
    def penalty_misordered_values(self):
        return self.context.options.penalty_misordered_values
