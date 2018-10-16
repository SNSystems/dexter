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
  int bar = 0;
  if (a) { // DexWatch('bar')
    if (beards(1)) {
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

// bar down the a=false path gets lost here
merge:
  if (bar == 2) // DexWatch('bar')
    return beards(3);
  else
    return beards(4);
}

// DexExpectWatchValue('bar', '0', '2')

int
main()
{
  return foo(false, true);
}
