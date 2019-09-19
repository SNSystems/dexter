// RUN: %dexter -- -fno-unroll-loops
int
foo(int blah)
{
  int i = 0;
  for (i = blah; i < blah + 10; i++) { // DexWatch('i', 'blah')
    if (i < 3)  // DexWatch('i', 'blah')
      return 0; // DexUnreachable()
  }
  return 1; // DexWatch('i', 'blah')
}

int
main()
{
  return foo(3);
}

// And at O2 we just can't read those variables, despite a relatable indvar
// being available.
// This seems poor codegen because we compare two constant values in the loop
// which is exactly what I was expecting indvars to get rid of, see the
// loop-invariant-conditions.ll test in llvm

// DexExpectWatchValue('blah', '3', from_line=1, to_line=50)
// DexExpectWatchValue('i', '0', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 2)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
