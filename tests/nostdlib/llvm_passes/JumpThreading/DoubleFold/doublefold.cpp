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
foo(bool a, int fudge)
{
  int lala = 0;
  if (a) { // DexExpectStepOrder(1)
    lala = beards(4); // DexExpectStepOrder(2)
    if (a) {
      fudge += 12; // DexExpectStepOrder(3)
    } else {
      fudge += 1; // DexUnreachable()
    }
  } else {
    lala = beards(5); // DexUnreachable()
    fudge += 24;      // DexUnreachable()
  }

  return lala + fudge; // DexExpectStepOrder(4)
}

int
main()
{
  return foo(true, 3);
}
