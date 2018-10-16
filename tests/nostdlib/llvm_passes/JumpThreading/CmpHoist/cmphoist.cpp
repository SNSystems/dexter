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
foo(bool a, int fudge, int lala)
{
// Just test that the steps in this func proceed as expected
  bool loljmp = false;
  if (a) { // DexExpectStepOrder(1)
    loljmp = fudge == 12; // DexExpectStepOrder(2)
  } else {
    loljmp = fudge == 18; // DexUnreachable()
  }

  if (loljmp) { // DexExpectStepOrder(3)
    return beards(lala + 3); // DexUnreachable()
  } else {
    return beards(lala / 5); // DexExpectStepOrder(4)
  }
}

int
main()
{
  return foo(true, 3, 4);
}
