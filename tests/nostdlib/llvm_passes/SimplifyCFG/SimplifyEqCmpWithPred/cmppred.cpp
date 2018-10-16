// RUN: %dexter
// This will combined by -mem2reg -simplifycfg into just one branch.
int
main()
{
  volatile int foo = 4;   // DexWatch('foo')

  int read = foo;         // DexWatch('foo')

  if (read == 4) {        // DexWatch('foo', 'read')
    foo = 5;              // DexWatch('foo', 'read')
  }                       // DexWatch('foo', 'read')
  if (read == 4) {        // DexWatch('foo', 'read')
    foo += 8;             // DexWatch('foo', 'read')
  }                       // DexWatch('foo', 'read')

  return foo;             // DexWatch('foo', 'read')
}

// XXX -- foo gains the value '5' on the line where it's assigned, which isn't
// technically correct, but dexter can't describe 'value appeared too early'.

// DexExpectWatchValue('foo', '4', '5', '13', from_line=6, to_line=17)
// DexExpectWatchValue('read',  '4', from_line=6, to_line=17)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('BACKWARD', 0)
// Dex notreally ExpectStepKind('FORWARD', 5)
// DexExpectStepKind('FUNC', 1)
