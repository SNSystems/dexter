// RUN: %dexter
int global = 0;

int
foo(int bar)       // DexWatch('bar', 'global')
{
  int lolret = 0;  // DexWatch('bar', 'global', 'lolret')
  if (bar & 1) {   // DexWatch('bar', 'global', 'lolret')
    bar += 1;      // DexUnreachable()
    lolret += 1;   // DexUnreachable()
  } else {         // DexWatch('bar', 'global', 'lolret')
    global = 2;    // DexWatch('bar', 'global', 'lolret')
    lolret += 2;   // DexWatch('bar', 'global', 'lolret')
  }                // DexWatch('bar', 'global', 'lolret')

  if (bar & 2) {   // DexWatch('bar', 'global', 'lolret')
    bar += 2;      // DexUnreachable()
    lolret += 3;   // DexUnreachable()
  } else {         // DexWatch('bar', 'global', 'lolret')
    global = 5;    // DexWatch('bar', 'global', 'lolret')
    lolret += 4;   // DexWatch('bar', 'global', 'lolret')
  }                // DexWatch('bar', 'global', 'lolret')

  return lolret;   // DexWatch('bar', 'global', 'lolret')
}

int
main()
{
  volatile int baz = 4;
  int read = baz;          // DexWatch('global')
  int lolret2 = foo(read);  // DexWatch('global', 'read')
  return global + lolret2;  // DexWatch('global', 'read', 'lolret2')
}

// Here, mergeConditionalStores merges the two accesses to global into one,
// with some kind of select arrangement beforehand. Run in O2, we get a ton
// of backwards steps, stepping over unreachable lines, illegal values for
// lolret, amoungst other things.
// It gets even worse if you just run with opt -mem2reg -simplifycfg.
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38756
// As of 2018-10-8, the illegal value is fixed, but we still step on
// unreachable lines.

// DexExpectWatchValue('bar', '4', from_line=1, to_line=50)
// DexExpectWatchValue('lolret', '0', '2', '6', from_line=1, to_line=50)
// DexExpectWatchValue('global', '0', '2', '5', from_line=1, to_line=50)
// DexExpectWatchValue('lolret2', '6', from_line=1, to_line=50)
// DexExpectWatchValue('read', '4', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 3)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
