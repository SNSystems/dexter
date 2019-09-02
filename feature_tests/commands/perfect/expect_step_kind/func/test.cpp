// Purpose:
//      Check that \DexExpectStepKind correctly counts 'FUNC' steps for a
//      trivial test. Expect one 'FUNC' per call to a function which is defined
//      in one of the source files in the test directory.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w  \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: func:

int func(int i) {
    return i;
}

int main()
{
    func(0);
    func(1);
    return 0;
}

// main, func, func
// DexExpectStepKind('FUNC', 3)
