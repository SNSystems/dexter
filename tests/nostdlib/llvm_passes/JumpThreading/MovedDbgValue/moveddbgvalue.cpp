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
  int fudge = 0;
  if (a) {              // DexWatch('fudge')
    lala = beards(4);   // DexUnreachable()
    fudge = 12;         // DexUnreachable()
  } else {
    lala = beards(5);   // DexWatch('fudge')
    fudge = 24;         // DexWatch('fudge')
  }

  fudge += 3; // DexWatch('fudge')

// All paths get the value 15 for fudge. This is probably a duplicate of
// PR38754, but as it's done purely with constants, worth checking out

  if (a && b && c) {    // DexWatch('fudge')
    return beards(lala + fudge); // DexUnreachable()
  } else {
    return beards(lala + fudge + lolglobal++); // DexWatch('fudge')
  }
}

// DexExpectWatchValue('fudge', '0', '24', '27')

int
main()
{
  return foo(false, true, true);
}
