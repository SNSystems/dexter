// RUN: %dexter
int
main()
{
  volatile int foo = 4;

  if (foo == 0)  // DexWatch('foo')
    return 8;    // DexUnreachable()
  else
    return 4;    // DexWatch('foo')
}

// DexExpectWatchValue('foo', '4', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
