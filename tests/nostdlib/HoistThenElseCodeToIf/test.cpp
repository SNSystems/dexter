int g_a = 1;
int g_b = 2;
int g_c = 1;
void external(int, int);
static void fn_1()
{
  int x = g_a + g_b;
  int y = g_a * g_b;  // DexWatch("x")
  external(x, y);     // DexWatch("x", "y")
}
static void fn_2()
{
  int x = g_a + g_b;
  int y = g_a * g_a * g_b * g_b;
  external(x, y);
}
int main()
{
  if (g_c)
    fn_1();
  else
    fn_2();
  return 0;
}

// Common code is hoisted. The merged instr is given line 0. This test
// doesn't show much except that simplifycfg does a thing after inlining
// something.

// DexExpectWatchValue("x", 3, from_line=8, to_line=9)
// DexExpectWatchValue("y", 2, on_line=9)

// Test run:
// python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g" -v
// HoistThenElseCodeToIf: (1.0000)
//
// python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g" -v
// HoistThenElseCodeToIf: (0.1429)
