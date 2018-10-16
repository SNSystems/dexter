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
  int bar = 0;
  if (somenum == 0) { // DexExpectStepOrder(1)
    bar += beards(2); // DexUnreachable()
  }

  // On jump threading, entry to foo lands at the != if condition and bar is
  // zero, a state of the program that isn't necessarily true if somenum == 0.
  if (somenum != 0) {
    bar += beards(3); // DexExpectStepOrder(2, 3)
  }

  return bar; // DexExpectStepOrder(4)
}

int
main()
{
  return foo(42);
}
