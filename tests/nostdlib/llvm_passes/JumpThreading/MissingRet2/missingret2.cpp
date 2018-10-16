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
  int someval = beards(4); // DexExpectStepOrder(1)
  if (someval == 4) {
    b = true;
    someval = 12;
  }

  if (someval == 4) {
    return someval;
  } else {
    // This ret becomes unconditional, but not stepped on
    // step is before $rax is loaded too
    return 0; // DexExpectStepOrder(2)
  }
}

int
main()
{
  return foo(true, true);
}
