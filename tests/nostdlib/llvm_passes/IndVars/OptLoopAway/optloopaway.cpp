// RUN: %dexter -- -fno-unroll-loops
int
main()
{
  for (unsigned int i = 0; i < 10; i++) {
    if (i > 11)  // DexExpectStepOrder(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
      return 0;
  }
  return 1; // DexExpectStepOrder(11)
} // DexExpectStepOrder(12)

// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
