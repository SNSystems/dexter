// RUN: %dexter
int
bees()
{
  volatile int bar = 12; // DexUnreachable()
  return bar;            // DexUnreachable()
}

int
main()
{
  volatile int foo = 4;
  int read1 = foo;
  int brains = foo;        // DexWatch('read1')

  int trains = 0;          // DexWatch('read1', 'brains')
  if (read1 > 3) {         // DexWatch('read1', 'brains', 'trains')
    int tony = brains * 3; // DexWatch('read1', 'brains', 'trains')
    if (tony > 20) {       // DexWatch('read1', 'brains', 'trains', 'tony')
      trains = bees();     // DexUnreachable()
    }                      // DexWatch('read1', 'brains', 'trains', 'tony')
  }                        // DexWatch('read1', 'brains', 'trains')

  return trains;           // DexWatch('read1', 'brains', 'trains')
}

// This tests for the FoldBranchToCommonDest optimisation, which (if you
// add -debug to opt) does trigger, however it appears that when lowered to
// X86 the backend undoes it.
// Either way, all the line numbers related to the inner condition get lost
// in clang-7.0

// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectWatchValue('brains', '4', from_line=1, to_line=50)
// DexExpectWatchValue('trains', '0', from_line=1, to_line=50)
// DexExpectWatchValue('tony', '12', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
