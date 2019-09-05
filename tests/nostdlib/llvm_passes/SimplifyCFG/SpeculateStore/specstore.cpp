// RUN: %dexter
int
foo(int *blah, int lala, int trains)  // DexWatch('*blah', 'lala', 'trains')
{                                     // DexWatch('*blah', 'lala', 'trains')
  trains *= 12;                       // DexWatch('*blah', 'lala', 'trains')
  *blah = trains;                     // DexWatch('*blah', 'lala', 'trains')
  if (lala) {                         // DexWatch('*blah', 'lala', 'trains')
    *blah = lala + trains + 3;        // DexWatch('*blah', 'lala', 'trains')
  }                                   // DexWatch('*blah', 'lala', 'trains')
  return 0;                           // DexWatch('*blah', 'lala', 'trains')
}

int
main()
{
  int fgasdf = 1;
  foo(&fgasdf, 1, 3);                // DexWatch('fgasdf')
  return fgasdf;                     // DexWatch('fgasdf')
}

// Store speculation excitingly inverts the control flow of foo, with two
// backwards steps
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38769

// DexExpectWatchValue('fgasdf', '1', '40', from_line=1, to_line=50)
// DexExpectWatchValue('*blah', '1', '36', '40', from_line=1, to_line=50)
// DexExpectWatchValue('trains', '3', '36', from_line=1, to_line=50)
// DexExpectWatchValue('lala', '1', from_line=1, to_line=50)
// DexExpectStepKind('FUNC', 3)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
