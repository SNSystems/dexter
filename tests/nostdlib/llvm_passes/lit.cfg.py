import os

import lit.formats

from lit.llvm.subst import ToolSubst
from lit.llvm import llvm_config

#PATHTODEXTER='/fast/fs/dexter/dexter.py'
PATHTODEXTER='/home/jmorse/dexter_gh/dexter.py'
PATHTOTESTER='/home/jmorse/dextests/dexwrapper.sh'

config.name = 'DexTests'
config.test_format = lit.formats.ShTest(False)
config.suffixes = ['.cpp']
config.test_source_root = os.path.dirname(__file__)
config.test_exec_root = os.path.dirname(__file__) # XXX dexter-results-dir?

if 'opt' not in lit_config.params:
    raise Exception('Please specify opt={0,2} with --param')
optlevel = '-O{}'.format(lit_config.params['opt'])

if 'clang' in lit_config.params:
    clang_location = lit_config.params['clang']
    config.environment['PATHTOCLANG'] = clang_location

options = '-fno-inline -g {}'.format(optlevel)

config.substitutions.append(('%dexter', '{} {} test --debugger lldb --builder clang --cflags "{}" .'.format(PATHTOTESTER, PATHTODEXTER, options)))
