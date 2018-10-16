// RUN: %dexter
int
foo(int *blah, int lala, int trains) // DexWatch('*blah', 'lala', 'trains')
{                                    // DexWatch('*blah', 'lala', 'trains')
  trains *= 12;                      // DexWatch('*blah', 'lala', 'trains')
  *blah = trains;                    // DexWatch('*blah', 'lala', 'trains')
  if (lala == 1) {                   // DexWatch('*blah', 'lala', 'trains')
    int tmp = lala + trains;         // DexWatch('*blah', 'lala', 'trains')
    *blah = tmp;                     // DexWatch('*blah', 'lala', 'trains', 'tmp')
  }                                  // DexWatch('*blah', 'lala', 'trains')
  return 0;                          // DexWatch('*blah', 'lala', 'trains')
}

int
main()
{
  int fgasdf = 1;
  foo(&fgasdf, 1, 3);  // DexWatch('fgasdf')
  return fgasdf;       // DexWatch('fgasdf')
}

// Add to calculate tmp never happens, because condition gets folded into the
// false branch.

// DexExpectWatchValue('fgasdf', '1', '37', from_line=1, to_line=50)
// DexExpectWatchValue('*blah', '1', '36', '37', from_line=1, to_line=50)
// DexExpectWatchValue('trains', '3', '36', from_line=1, to_line=50)
// DexExpectWatchValue('lala', '1', from_line=1, to_line=50)
// DexExpectWatchValue('tmp', '37', from_line=1, to_line=50)
// DexExpectStepKind('FUNC', 3)
// DexExpectStepKind('BACKWARD', 0)
