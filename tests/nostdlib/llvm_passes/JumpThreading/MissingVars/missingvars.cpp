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
  int someval = beards(4); // DexWatch('a', 'b')
  if (a) {                 // DexWatch('a', 'b')
    b = true;              // DexWatch('a', 'b')
    someval = 12;          // DexWatch('a', 'b')
  }

  bool c = someval == 12;  // DexWatch('a', 'b')
  // Both b and c go missing here despite being in regs
  if (b ^ c) {             // DexWatch('a', 'b', 'c')
    return someval;
  } else {
    return -1;
  }
}

// DexExpectWatchValue('a', 'true')
// DexExpectWatchValue('b', 'true')
// DexExpectWatchValue('c', 'true')

int
main()
{
  return foo(true, true);
}
