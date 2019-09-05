// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;
  int read2 = foo;      // DexWatch('read1')

  switch ((read1 == 4) ? 3 : 1) {   // DexWatch('read1', 'read2')
  case 1:              // DexUnreachable()
    read1 *= read2;    // DexUnreachable()
    break;             // DexUnreachable()
  case 3:              // DexWatch('read1', 'read2')
    read1 /= read2;    // DexWatch('read1', 'read2')
    break;             // DexWatch('read1', 'read2')
  }                    // DexWatch('read1', 'read2')

  return read1;        // DexWatch('read1', 'read2')
}

// SimplifySwitchOnSelect folds the switch into the if condition, which seems
// to go well, but we lose the divided value of read1 by the final ret insn
// on clang 7
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38773
// Fixed: https://reviews.llvm.org/rL343445

// DexExpectWatchValue('read1', '4', '1', from_line=1, to_line=50)
// DexExpectWatchValue('read2', '4', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
