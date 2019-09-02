// Purpose:
//      Check that \DexExpectStepKind correctly counts 'BACKWARD' steps for a
//      trivial test. Expect one 'BACKWARD' for every step onto a lesser source
//      line number in the same function. Expect one 'FORWARD' for every step
//      onto a greater source line number in the same function.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w  \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: direction:

int main()
{
    for (int i = 0; i < 2; ++i) {
        i = i;
    }
    return 0;
}

// DexExpectStepKind('BACKWARD', 2)
// DexExpectStepKind('FORWARD', 3)
