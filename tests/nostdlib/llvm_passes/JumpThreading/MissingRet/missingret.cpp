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
  int bar;
  if (a) { // DexExpectStepOrder(1)
    if (beards(0)) { // DexExpectStepOrder(2)
      bar = 2;    // DexUnreachable()
      goto merge; // DexUnreachable()
    } else {
      // This return line is missed, despite having its own block?
      // The insn stepped onto hasn't yet loaded $rax either
      return 1; // DexExpectStepOrder(3)
    }
  } else {
    if (b) {         // DexUnreachable()
      bar = 2;       // DexUnreachable()
      goto merge;    // DexUnreachable()
    } else {         // DexUnreachable()
      bar = 3;       // DexUnreachable()
      goto merge;    // DexUnreachable()
    }
  }

merge:
  if (bar == 2) // DexUnreachable()
    return beards(3); // DexUnreachable()
  else // DexUnreachable()
    return beards(4); // DexUnreachable()
}

int
main()
{
  return foo(true, true);
}
