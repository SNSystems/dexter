// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;

  bool lolwat1 = read1 == 1;
  bool lolwat2 = read1 == 2;
  if (lolwat1 || lolwat2) // DexWatch('read1')
    read1 += 4;   // DexWatch('read1')

  return read1;   // DexWatch('read1')
}

// Should (TM) hit tryToSimplifyUncondBranchWithICmpInIt, folds default case
// out. Not really expecing anything interesting, but does feature a backwards
// jump

// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)

