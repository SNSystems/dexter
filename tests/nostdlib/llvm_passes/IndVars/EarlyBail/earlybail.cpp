// RUN: %dexter -- -fno-unroll-loops
int
foo(int blah)
{
  int i = 0;
  for (i = blah; i < blah + 10; i++) { // DexWatch('i', 'blah')
    if (i < -1)  // DexWatch('i', 'blah')
      return 0; // DexUnreachable()
    if (i == blah + 3) // DexWatch('i', 'blah')
      goto fail;       // DexWatch('i', 'blah')
  }

  if (0) { // DexUnreachable()
  fail:
    return 3;
  }

  return i; // DexWatch('i', 'blah')
}  // DexWatch('i', 'blah')

int
main()
{
  volatile int bar = 3;
  return foo(bar);
}

// Indvars can statically determine that if i is >= -1, then we will guarantee
// exit through the fail branch, which means returning three. The whole func
// is thus optimised into being an 'if', all debug data is dropped, and we
// end up on the final line with 'i' unmodified, reporting a value it would
// never have on the exit from the function

// DexExpectWatchValue('blah', '3', from_line=1, to_line=50)
// DexExpectWatchValue('i', '0', '3', '4', '5', '6',  from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 3)
// DexExpectStepKind('FUNC', 3)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
