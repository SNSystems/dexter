int g_a = 0;
int run_loop();
int do_something();

static bool condition(int c)
{
  return c > 4; // DexWatch("c")
}
int main()
{
  int x = 0;
  while (run_loop())
  {
    if (condition(++x))
      break;
    do_something();
  }

  return g_a;
}

// condition(..) is folded into the while header after inlining.

// DexExpectWatchValue("c", "1", "2", "3", "4", "5", on_line=7)

// Test run:
// python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g" -v
// FoldBranchToCommonDest: (1.0000)
//
// python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g" -v
// FoldBranchToCommonDest: (0.0000)
