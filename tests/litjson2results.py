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
    if 'metrics' in x:
      metric = x['metrics']['score']
    else:
      metric = "NaN"
    name = x['name']
    print('{},{}'.format(name, metric))
