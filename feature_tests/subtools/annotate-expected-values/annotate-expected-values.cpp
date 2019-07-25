// Purpose:
//      Check the `annotate-expected-values` subtool works with typical inputs.
//
// REQUIRES: linux, clang, lldb
//
// # Build test case, save results in tmp folder `%t`
// RUN: dexter.py test -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" \
// RUN:     --results %t -- %S
//
// # Run annotate-expected-values on a copy of this file
// RUN: cp %s %t/out.cpp
// RUN: dexter.py annotate-expected-values %t/annotate-expected-values.dextIR \
// RUN:     %t/out.cpp
//
// # Remove CHECK lines from the copy for FileCheck
// RUN: grep -v "CHECK" %t/out.cpp | FileCheck %s
//
// # Check that new commands have been added
// CHECK-DAG: ExpectStepKind(
// CHECK-DAG: ExpectWatchValue(
//
// # Tidy up
// # [TODO] This doesn't run if FileCheck fails!
// RUN: rm -rf %t


int main() {
    int a = 0;
    return 0;   // DexWatch('a')
}
