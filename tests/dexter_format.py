import csv
import math
import os
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import lit.formats
import lit.Test
import lit.TestRunner as TestRunner

PATHTODEXTER='{}/../dexter.py'.format(os.path.dirname(__file__))
PATHTOTESTER='{}/dexwrapper.sh'.format(os.path.dirname(__file__))

def get_dexter_substitution(config):
  return '{} {} test --results-directory %T --debugger {} --builder {} --cflags "{}" .'.format(PATHTOTESTER, PATHTODEXTER, config.dexter_debugger, config.dexter_builder, config.dexter_cflags)

class DexterFormat(lit.formats.ShTest):
    def execute(self, test, lit_config):
      result = lit.TestRunner.executeShTest(test, lit_config, False, [('%dexter', get_dexter_substitution(test.config))])
      tmpDir, tmpBase = TestRunner.getTempPaths(test)
      try:
        with open(tmpDir + '/summary.csv', 'r') as f:
          lines = f.readlines()
          reader = csv.reader(lines)
          rows = [x for x in reader]
          assert len(rows) == 2
          metric = float(rows[1][1])
        if math.isnan(metric):
          result = lit.Test.Result(lit.Test.FAIL, 'Test returned nan')
        else:
          result.addMetric('score', lit.Test.RealMetricValue(metric))
      except IOError:
        msg = 'Failed to open summary from {}'.format(tmpDir)
        result = lit.Test.Result(lit.Test.UNSUPPORTED, msg)
      return result
