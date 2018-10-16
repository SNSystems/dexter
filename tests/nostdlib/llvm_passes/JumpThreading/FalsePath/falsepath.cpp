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
foo(int somenum)
{
  int bar = somenum;
  if (somenum == 0) { // DexExpectStepOrder(1)
    bar += beards(2);
  }

  if (somenum != 0) {
    // Just test that we actually step on this line
    bar += (somenum + 12) & 0xffff; // DexExpectStepOrder(2)
  }

  return bar; // DexExpectStepOrder(3)
}

int
main()
{
  return foo(1);
}
