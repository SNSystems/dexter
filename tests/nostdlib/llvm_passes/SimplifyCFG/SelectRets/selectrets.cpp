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
  } else {
    return -1;          // DexUnreachable()
  }
}  // DexExpectStepOrder(5)

// This test, when optimised, compiles all the tests down into conditional
// moves on x86, thus making any line numbers with 'return' on them likely
// inaccurate. The slightly bad score for O2 is thus expected

// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
