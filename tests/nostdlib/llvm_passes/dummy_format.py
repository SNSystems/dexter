import csv
import os
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import lit.formats
import lit.Test
import lit.TestRunner as TestRunner

class DummyFormat(lit.formats.ShTest):
    def execute(self, test, lit_config):
      result = super(DummyFormat, self).execute(test, lit_config)
      tmpDir, tmpBase = TestRunner.getTempPaths(test)
      with open(tmpDir + '/summary.csv', 'r') as f:
        lines = f.readlines()
        reader = csv.reader(lines)
        rows = [x for x in reader]
        assert len(rows) == 2
        metric = float(rows[1][1])
      result.addMetric('score', lit.Test.RealMetricValue(metric))
      return result
