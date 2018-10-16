// RUN: %dexter
int
main()
{
  volatile int foo = 0;

  int beards = 0;
  if (foo == 4)   // DexWatch('beards')
    beards = 8;   // DexUnreachable()
  else
    beards = 4;   // DexWatch('beards')

  return beards;  // DexWatch('beards')
}

// DexExpectWatchValue('beards', '0', '4', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
