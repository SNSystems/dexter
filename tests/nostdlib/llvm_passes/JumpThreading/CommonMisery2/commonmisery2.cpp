// RUN: %dexter -- -mllvm -max-speculation-depth=0
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
  if (somenum == 0) {
    bar += beards(2);
  }

  // On jump threading, entry to foo lands at the != if condition and bar is
  // zero, a state of the program that isn't necessarily true if somenum == 0.
  if (somenum != 0) { // DexWatch('bar')
    bar += beards(3);
  }

  return bar;
}

// DexExpectWatchValue('bar', '2')
// We only get an unexpected result with -mllvm -max-speculation-depth=0
// Still an error IMO, simplifycfg just covers it.

int
main()
{
  return foo(0);
}
