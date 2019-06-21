int g_a = 5;
static bool fn(int x)
{
  return (x == 1 || x == 5);        // DexWatch("x")
}
static bool fn_2(int y)
{
  return (y == 7 || fn(y));         // DexWatch("y")
}
static bool fn_3(int z)
{
  return (z == 25 || fn_2(z));      // DexWatch("z")
}
int main()
{
  if(fn_3(g_a))
    g_a = 0;
  return 0;
}

// After inlining the chain of ICmp instructions is folded into a switch.
// This is obviously a very trivial example but debug info _is_ dropped
// directly as a result of simplifycfg after inlining.
// Having DexExpectedCallStack(..) here would be useful.

// DexExpectWatchValue("x", "5", on_line=4)
// DexExpectWatchValue("y", "5", on_line=8)
// DexExpectWatchValue("z", "5", on_line=12)

// Test run:
// python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g" -v
// SimplifyBranchOnICmpChain: (1.0000)
//
// python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g" -v
// SimplifyBranchOnICmpChain: (0.4286)