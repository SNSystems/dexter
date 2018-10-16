// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read = foo;
  int read1 = foo;        // DexWatch('read')

  int result = 0;         // DexWatch('read', 'read1')
  if (read == 4) {        // DexWatch('read', 'read1', 'result')
    result = read1 + 2;   // DexWatch('read', 'read1', 'result')
  } else {                // DexWatch('read', 'read1', 'result')
    result = read1 - 2;   // DexWatch('read', 'read1', 'result')
  }                       // DexWatch('read', 'read1', 'result')

  return result;          // DexWatch('read', 'read1', 'result')
}

// dbg.value's seemly get/got hoisted without guarding form inside the
// speculated BBs here.
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38763
// Fixed: https://reviews.llvm.org/rL342527

// DexExpectWatchValue('read', '4', from_line=1, to_line=50)
// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectWatchValue('result', '0', '6', from_line=1, to_line=50)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('BACKWARD', 0)
