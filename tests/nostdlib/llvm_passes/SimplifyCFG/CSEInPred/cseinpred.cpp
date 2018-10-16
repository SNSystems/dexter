// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;
  int read2 = foo;
  int read3 = foo;
  int read4 = foo;            // DexWatch('foo', 'cheese')
  // see below for cheese read
  int cheese = foo;           // DexWatch('foo')
  int a = read1 + read2;      // DexWatch('foo', 'cheese')
  a += cheese;                // DexWatch('foo', 'cheese', 'a')

  if (foo == 0) {             // DexWatch('foo', 'cheese', 'a')
    a %= cheese * 12;         // DexUnreachable()
    cheese = read1 + read2;   // DexUnreachable()
    a += cheese - 12;         // DexUnreachable()
    a *= 20;                  // DexUnreachable()
    a /= 3;                   // DexUnreachable()
  } else {                    // DexWatch('foo', 'cheese', 'a')
    a += read3;               // DexWatch('foo', 'cheese', 'a')
    a -= read4;               // DexWatch('foo', 'cheese', 'a')
    a %= (read3 + read4);     // DexWatch('foo', 'cheese', 'a')
    a += cheese;              // DexWatch('foo', 'cheese', 'a')
  }                           // DexWatch('foo', 'cheese', 'a')

  return a;                   // DexWatch('foo', 'cheese', 'a')
}

// The idea here was that SimplifyCFG would CSE read1 + read2 into the
// predecessor of the false branch, and potentally dbg.value label 'cheese'
// with the wrong value prior to the branch. And that does seem to be the
// case if you print out 'cheese' prior to the branch insns, but on lines
// where the value is formally undefined.
//
// I've kept that as a dexter failure: we step down to the first assignment to
// 'a', then backwards to the read3/4 assignments, so during that time someone
// would legitimately believe that cheese was available for inspection, and
// will get an illegal value.
//
// Plus, a trainwreck of stuff seems to turn up in the true branch where
// all the values appear early or wrong, so test that too.

// DexExpectWatchValue('foo', '4', from_line=1, to_line=50)
// DexExpectWatchValue('cheese', '4', from_line=1, to_line=50)
// DexExpectWatchValue('a', '8', '12', '16', '12', '4', '8', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
