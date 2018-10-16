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
foo(int bar)
{
  if (bar < 5) { // DexExpectStepOrder(1)
    beards(1); // DexExpectStepOrder(2)
  } else {
    beards(2);
  }

  beards(3); // DexExpectStepOrder(4)
  // Jump threading means 'bar' is optimized out by this point,
  // and we don't see either the test or the call to the lower values.
  // This is similar to other tests, but more concise...
  if (bar < 5) {
    return beards(4); // DexExpectStepOrder(6, 7)
  } else {
    return beards(5);
  }
}

int
main()
{
  return foo(3);
}
