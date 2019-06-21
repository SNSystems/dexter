int g_a = 25;
int g_b = 7;
int g_c = 0;
__attribute__((always_inline))
static int fn_a(unsigned i)
{
  i %= 5;                           // DexWatch("i")
  int array[] {1, 3, 5, 25, 28};    // DexWatch("i")
  return array[i];                  // DexWatch("i")
}
int main()
{
  if (g_a == fn_a(0)
   || g_a == fn_a(1)
   || g_a == fn_a(2)
   || g_a == fn_a(g_b))
    g_c = g_a;

  return g_c;
}

// After inlining FoldValueComparisonIntoPredecessors folds g_a == fn_a(0),
// g_a == fn_a(1), and g_a == fn_a(2) into one switch.
// g_b value is "unknown" so this cond can't be folded (maybe this is muddying
// the waters unnecessarily).

// DexExpectWatchValue("i", "0", "1", "2", "7", on_line=7)
// DexExpectWatchValue("i", "0", "1", "2", "2", from_line=8, to_line=9)

// Test run:
// python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g" -v
// FoldValueComparisonIntoPredecessors: (1.0000)
//
// python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g" -v
// FoldValueComparisonIntoPredecessors: (0.1429)
