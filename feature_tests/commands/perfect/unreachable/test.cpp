// Purpose:
//    Check that \DexUnreachable has no effect if the command line is never
//    stepped on.
//
// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: unreachable:

int main()
{
  return 0;
  return 1; // DexUnreachable()
}
