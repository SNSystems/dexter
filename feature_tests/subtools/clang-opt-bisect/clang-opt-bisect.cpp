// Purpose:
//     Check the `clang-opt-bisect` tool runs with typical input.
//
// REQUIRES: linux, clang, lldb
//
// RUN: true
// RUN: dexter.py clang-opt-bisect --debugger lldb --builder clang \
// RUN:     --cflags "-O0 -g" -- %S \
// RUN:     | FileCheck %s
// CHECK: running pass 0
// CHECK: wrote{{.*}}per_pass_score
// CHECK: wrote{{.*}}pass-summary
// CHECK: wrote{{.*}}overall-pass-summary

int main() {
    return 0;
}
