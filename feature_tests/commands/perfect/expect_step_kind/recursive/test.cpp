// Purpose:
//      Check that \DexExpectStepKind correctly handles recursive calls.
//      Specifically, ensure recursive calls count towards 'FUNC' and not
//      'BACKWARD'.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w  \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: recursive:

void func(int i) {
    if (i > 1)
        func(i - 1);
    return;
}

int main()
{
    func(3);
    return 0;
}

// main, func, func, func
// DexExpectStepKind('FUNC', 4)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FORWARD', 6)
