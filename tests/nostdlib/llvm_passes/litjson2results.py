#!/usr/bin/env python3

import json
import re
import sys

score = re.compile('^([A-Za-z0-9]+): \(([\.0-9]+)\)$')

if len(sys.argv) > 1:
    if len(sys.argv) != 2:
        raise Exception("Unexpected cmdline options")
    f = open(sys.argv[1], 'r')
else:
    f = sys.stdin

# stdin (or file) -> stdout
dump = json.load(f)
for x in dump['tests']:
    output = x['output'].split('\n')
    for y in output:
      m = score.match(y)
      if m is not None:
        assert m.group(1) in x['name'] # Ensure we picked out the name correctly
        print('{},{}'.format(m.group(1), m.group(2)))
