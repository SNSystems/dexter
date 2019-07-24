// Purpose:
//      Check that \DexExpectStepKind applies no penalties when there are no
//      unexpected step kinds.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w  \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: expect_step_kinds:

#include <cstdlib>

int wrapper_abs(int i){
    return abs(i);
}

int main()
{
    volatile int x = 2;
    for (int i = 0; i < x; ++i) {
        wrapper_abs(i);
    }
    return 0;
}

// DexExpectStepKind('FUNC', 5)
// DexExpectStepKind('FUNC_EXTERNAL', 2)
// DexExpectStepKind('BACKWARD', 2)
