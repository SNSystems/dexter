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
  if (somenum == 42) { // DexExpectStepOrder(1)
    if (somenum == 43) { // Gets threaded away
      return -((beards(100) & 15) + 12); // DexUnreachable()
    } else {
      return ((beards(100) & 15) + 12); // DexExpectStepOrder(2)
      // This return, which is executed, seems to be eliminated from the line
      // table because it's CSE'd with the prior return, which is DCE'd. This
      // leads to a mildly suboptimal jump from (somenum == 42) into beards().
    }
  } else {
    return 11; // DexUnreachable()
  }
}

int
main()
{
  return foo(42);
}
