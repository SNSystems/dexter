// RUN: %dexter
int
main()
{
  volatile int foo = 0;
  int read1 = foo; // DexExpectStepOrder(1)

  int beards = 0;
  if (foo == 4)    // DexExpectStepOrder(2)
    beards = 8;    // DexUnreachable()
  else
    beards = 4;    // DexExpectStepOrder(3)

  return beards;   // DexExpectStepOrder(4)
}

