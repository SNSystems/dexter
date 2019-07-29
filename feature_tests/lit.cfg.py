import os
import sys

import lit.util
import lit.formats

dexter_path, _ = os.path.split(os.path.dirname(__file__))

# name: The name of this test suite.
config.name = "DExTer feature tests"

# testFormat: The test format to use to interpret tests.
config.test_format = lit.formats.ShTest(True)

# suffixes: A list of file extensions to treat as test files. This is overriden
# by individual lit.local.cfg files in the test subdirectories.
config.suffixes = ['.cpp', '.c', '.test']

# excludes: A list of directories to exclude from the testsuite. The 'Inputs'
# subdirectories contain auxiliary inputs for various tests in their parent
# directories.
config.excludes = ['Inputs']

# test_source_root: The root path where tests are located.
config.test_source_root = os.path.dirname(__file__)

# Add Dexter to PATH.
config.environment['PATH'] += ":{}".format(dexter_path)

# test_exec_root: The root path where tests should be run.
# Test scripts will be cached here.
config.test_exec_root = os.path.join(dexter_path, 'build/lit')

# available_features: REQUIRES/UNSUPPORTED lit commands look at this list.
if sys.platform.startswith('linux'):
    config.available_features.add('linux')
else:
    config.available_features.add(sys.platform)

# Check clang is available.
# [TODO] clang-cl.exe / clang.exe for win32?
if lit.util.which('clang') is not None:
    config.available_features.add('clang')


# Check which debuggers are available:
# [TODO] Use dexter to verify which debuggers are available as this simple check
# doesn't know if the python interface is available, doesn't check .exe for
# win32 etc.
if lit.util.which('lldb') is not None:
    config.available_features.add('lldb')
