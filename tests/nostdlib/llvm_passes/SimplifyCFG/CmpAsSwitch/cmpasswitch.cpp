// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;

  if (read1 == 1 || read1 == 2 || read1 == 3 || read1 == 4) // DexWatch('read1')
    read1 += 4;   // DexWatch('read1')

  return read1;   // DexWatch('read1')
}

// This was an attempt to hit tryToSimplifyUncondBranchWithICmpInIt but it
// looks semi-impossible; leave this test here as it features a backwards step

// DexExpectWatchValue('read1', '4', '8', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)

