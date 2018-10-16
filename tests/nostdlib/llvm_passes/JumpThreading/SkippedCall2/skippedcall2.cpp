// RUN: %dexter
#include <stdbool.h>

int lolglobal = 1;

int
beards(int val)
{
  volatile int bar;
  bar = val;
  return bar;
}

int
foo(bool a, bool b)
{
  int bar;
  if (a) { // DexExpectStepOrder(1)
    if (beards(1)) { // DexExpectStepOrder(2, 3)
      bar = 2;
      goto merge;
    } else {
      return 1;
    }
  } else {
    if (b) {
      bar = 2;
      goto merge;
    } else {
      bar = 3;
      goto merge;
    }
  }

merge:
  if (bar == 2) // DexExpectStepOrder(4)
    return beards(3); // DexExpectStepOrder(5, 6)
    // We thread from the true-true block above to here, but
    // don't keep any line numbers. Plus, we tail call, so can't determine the
    // call site from inside beards(3)
  else
    return beards(4);
}

int
main()
{
  return foo(true, true);
}
