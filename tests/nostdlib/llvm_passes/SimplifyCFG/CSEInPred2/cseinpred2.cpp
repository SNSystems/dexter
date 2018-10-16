// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;
  int read2 = foo;
  int read3 = foo;
  int read4 = foo;

  int cheese = foo;           // DexWatch('foo')
  int a = read1 + read2;      // DexWatch('foo', 'cheese')
  a += read3 & 1;             // DexWatch('foo', 'cheese', 'a')
  a += cheese;                // DexWatch('foo', 'cheese', 'a')
  a += read4 & 1;             // DexWatch('foo', 'cheese', 'a')

  foo = 0;                    // DexWatch('foo', 'cheese', 'a')
  if (foo == 0) {             // DexWatch('foo', 'cheese', 'a')
    cheese = read1 + read2;   // DexWatch('foo', 'cheese', 'a')
    a -= cheese - 12;         // DexWatch('foo', 'cheese', 'a')
    a *= 20;                  // DexWatch('foo', 'cheese', 'a')
    a /= 3;                   // DexWatch('foo', 'cheese', 'a')
  } else {                    // DexWatch('foo', 'cheese', 'a')
    a += read3;               // DexUnreachable()
    a -= read4;               // DexUnreachable()
    a %= (read3 + read4);     // DexUnreachable()
    a += cheese;              // DexUnreachable()
  }                           // DexWatch('foo', 'cheese', 'a')

  return a;                   // DexWatch('foo', 'cheese', 'a')
}

// "cheese = read1 + read2" gets CSE'd into predecessor, but the debug info
// inexplicably doesn't pick up it's value _after_ entering the true branch.
// Corresponding CSEInPred  test has the opposite problem.
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38753

// DexExpectWatchValue('foo', '4', '0', from_line=1, to_line=50)
// DexExpectWatchValue('cheese', '4', '8', from_line=1, to_line=50)
// DexExpectWatchValue('a', '8', '12', '16', '320', '106', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
