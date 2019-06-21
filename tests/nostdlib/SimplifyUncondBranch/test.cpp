int external_3();
static int s_x;
static int s_y;
extern int g_a;

__attribute__((always_inline))
static int inline_me(int z)
{
  switch (z)
  {
    case 1:
      return external_3();
    case 2:
      return s_x; // DexWatch("s_x")
    case 3:
      return s_y; // DexWatch("s_y")
    default:
      return 5;
  }
}
int main()
{
  s_x = s_y = 5;
  int a = inline_me(g_a);     // g_a == 2
  int b = inline_me(g_a + 1); // g_a + 1 == 3
  return a + b;
}

// After inlining inline_me, case 2, 3, and default all contain a block which
// just returns 5. These returns become branches and simplifycfg will remove
// them when running SimplifyUncondBranch.

// test2.cpp: int g_a = 2;
// DexExpectWatchValue("s_x", "5", on_line=14)
// DexExpectWatchValue("s_y", "5", on_line=16)

// Test run:
// $ python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g"\
 -v -- tests/nostdlib/SimplifyUncondBranch
// SimplifyUncondBranch: (1.0000)

// $ python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g"\
 -v -- tests/nostdlib/SimplifyUncondBranch
// SimplifyUncondBranch: (0.2143)
