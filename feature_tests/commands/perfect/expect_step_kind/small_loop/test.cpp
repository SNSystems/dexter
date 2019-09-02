// Purpose:
//      Check that \DexExpectStepKind correctly counts function calls in loops
//      where the last source line in the loop is a call. Expect steps out
//      of a function to a line before the call to count as 'BACKWARD'.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w  \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: small_loop:

int func(int i){
    return i;
}

int main()
{
    for (int i = 0; i < 2; ++i) {
        func(i);
    }
    return 0;
}

// DexExpectStepKind('BACKWARD', 2)
