// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;
  int read2 = foo;   // DexWatch('read1')
  int read3 = foo;   // DexWatch('read1', 'read2')
  int brains = foo;  // DexWatch('read1', 'read2', 'read3')

  bool lolcond = read2 < 5;  // DexWatch('read1', 'read2', 'read3', 'brains')
  // Following cond is simply to force-CSE lolcond as an i1, so that its
  // calculation gets removed from one of the blocks further down.
  if (lolcond) {     // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
    read3 += 1;      // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
  }                  // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')

  if (read1 > 3) {   // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
    if (lolcond) {   // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
      brains *= 2;   // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
      brains += 1;   // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
    }                // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
  }                  // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')

  return brains + read3;  // DexWatch('read1', 'read2', 'read3', 'brains', 'lolcond')
}

// This should trigger SimplifyCondBranchToCondBranch, which prints
// "FOLDING BRs:[...]" in -debug, to select on the outcome of the relevant
// conditions. Various stepping orders go wrong, and we land on 'brains += 1'
// with an earlier valuation of brains (not tested for).
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38762

// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectWatchValue('read2', '4', from_line=1, to_line=50)
// DexExpectWatchValue('read3', '4', '5', from_line=1, to_line=50)
// DexExpectWatchValue('brains', '4', '8', '9', from_line=1, to_line=50)
// DexExpectWatchValue('lolcond', 'true', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
