// RUN: %dexter
int
main()
{
  volatile int foo = 4; // DexExpectStepOrder(1)
  int read1 = foo;      // DexExpectStepOrder(2)

  if (read1 == 5) {     // DexExpectStepOrder(3)
    return 8;           // DexUnreachable()
  } else if (read1 == 4) {
    return 1200000;     // DexExpectStepOrder(4)
  } else if (read1 == 60) {  // DexUnreachable()
    return 3;           // DexUnreachable()
  } else {              // DexUnreachable()
    return -1;          // DexUnreachable()
  }
} // DexExpectStepOrder(5)

// Here, we should be passing through the line 'return 1200000;', and the
// structure of the optimised program at O2 is sufficient for that to be
// represented and correct. However, it looks like we drop metadata when
// the returns are merged into a select/phi instruction.

// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
