// Purpose:
//      Check that \DexExpectStepOrder applies no penalty when the expected
//      order is found.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: expect_step_order:

int main()
{
  volatile int x = 1; // DexExpectStepOrder(1)
  volatile int y = 1; // DexExpectStepOrder(2)
  volatile int z = 1; // DexExpectStepOrder(3)
  return 0;
}
