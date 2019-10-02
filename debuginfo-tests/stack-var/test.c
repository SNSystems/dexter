// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang-c --debugger lldb --cflags "-O -glldb" -- %S

void __attribute__((noinline, optnone)) bar(int *test) {}
int main() {
  int test;
  test = 23;
  bar(&test); // DexLabel('before_bar')
  return test; // DexLabel('after_bar')
}

// DexExpectWatchValue('test', '23', on_line='before_bar')
// DexExpectWatchValue('test', '23', on_line='after_bar')

