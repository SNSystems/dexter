int external_1(int);
int external_2(int);

int something_1(int x)
{
  x = external_1(x);
  x = external_2(x);
  x = external_2(x);
  return external_1(x);
}

int something_2(int y)
{
  y = external_1(y);      // DexWatch("y")
  y = external_1(y);      // DexWatch("y")
  y = external_2(y);      // DexWatch("y")
  return external_1(y);   // DexWatch("y")
}

int main()
{
  volatile int Generator = 0;
  int z = Generator;

  if (z)
    /*-- This will get inlined --*/
    z = something_1(z);
  else
    /*-- This will get inlined --*/
    z = something_2(z);

  return z;
}

// This test stimulates simplifycfg's SinkCommonCodeFromPRedecessors(...).
//    lines [8, 9], [16, 17] are sunk in main() after inlining
//    sunk lines are given line 0 (since we're merging), therefore we expect O2
//    to knock out [16, 17] when stepping through main.
// It isn't the best inlining demo because it really focuses on simplifycfg.

// DexExpectWatchValue("y", "0", on_line=14)
// DexExpectWatchValue("y", "1", on_line=15)
// DexExpectWatchValue("y", "2", on_line=16) # Expect: simplifycfg sinks line 16 after inlining
// DexExpectWatchValue("y", "3", on_line=17) # Expect: simplifycfg sinks line 17 after inlining

// Test run:
// $ python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g"\
 -v -- tests/nostdlib/SinkCommonCodeFromPredecessors
// SinkCommonCodeFromPredecessors: (1.0000)

// $ python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g"\
 -v -- tests/nostdlib/SinkCommonCodeFromPredecessors
// SinkCommonCodeFromPredecessors: (0.5714)