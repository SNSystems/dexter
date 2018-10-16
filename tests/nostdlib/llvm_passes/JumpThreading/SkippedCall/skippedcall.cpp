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
foo(bool a, bool b, bool c)
{
  int lala = 0;
  if (a) { // DexExpectStepOrder(1)
    lala = beards(4); // DexExpectStepOrder(2, 3)
  } else {
    lala = beards(5);
  }

  if (a && b && c) { // DexExpectStepOrder(4)
    return beards(lala); // DexExpectStepOrder(5)
  } else {
    return beards(lala + lolglobal++);
  }
}

// We don't see the beards(lala) call because it's common'd with the later one

int
main()
{
  return foo(true, true, true);
}
