// RUN: %dexter
int
main()
{
  volatile int foo = 0;

  int beards = 0;
  if (foo == 4) // DexExpectStepOrder(1)
    beards = 8; // DexUnreachable()
  else
    beards = 4; // Reachable, but gets common'd, so not seen

  return beards; // DexExpectStepOrder(2)
}

// The unreachable beards = 8 assignment is stepped onto in this function,
// despite definitely never executing.
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=39187
