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
foo(bool a, bool b, bool c, int fudge)
{
  int lala = 0;        // DexWatch('fudge')
  if (a) {
    lala = beards(4);  // DexUnreachable()
    fudge += 12;       // DexUnreachable()
  } else {
    lala = beards(5);  // DexWatch('fudge')
    fudge += 24;       // DexWatch('fudge')
  }

  fudge += 3;          // DexWatch('fudge')

  if (a && b && c) {   // DexWatch('fudge')
    return beards(lala + fudge); // DexUnreachable()
  } else {
    return beards(lala + fudge + lolglobal++); // DexWatch('fudge')
  }
// Value of fudge completely screwed up here; likely a consequence of
// PR38754. Including base register!
} // DexWatch('fudge')

// DexExpectWatchValue('fudge', '3', '27', '30')

int
main()
{
  return foo(false, true, true, 3);
}
