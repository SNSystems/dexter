// Purpose:
//      Check that \DexUnreachable correctly applies a penalty if the command
//      line is stepped on.
//
// REQUIRES: linux, clang, lldb
//
// RUN: not dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: unreachable:

int
main()
{
  return 1;  // DexUnreachable()
}
