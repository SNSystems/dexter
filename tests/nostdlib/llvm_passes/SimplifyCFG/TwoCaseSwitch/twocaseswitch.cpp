// RUN: %dexter
int
main()
{
  volatile int foo = 4; // DexExpectStepOrder(1)
  int read1 = foo;      // DexExpectStepOrder(2)

  int bees;
  switch (read1) {      // DexExpectStepOrder(3)
  case 5:
    bees = 8;           // DexUnreachable()
    break;              // DexUnreachable()
  case 4:
    bees = 1200000;     // DexExpectStepOrder(4)
    break;
  default:
    bees = -1;          // DexUnreachable()
    break;              // DexUnreachable()
  }

  return bees; }  // DexExpectStepOrder(5)

// Stimulates ConvertTwoCaseSwitch, gets folded into two conditional moves
// on x86, thus step 4 will be optimised out. The others should not be seen.

// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
