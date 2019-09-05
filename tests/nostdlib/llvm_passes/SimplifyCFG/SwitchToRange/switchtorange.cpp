// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;

  int bar = 0;       // DexWatch('read1')
  switch (read1) {   // DexWatch('read1', 'bar')
  case 0:
  case 1:
  case 2:
  case 3:
    bar = 8;    // DexUnreachable()
    break;      // DexUnreachable()
  case 4:
  case 5:
  case 6:
  case 7:
  default:
    bar = 120000;  // DexWatch('read1', 'bar')
  }

  return bar; // DexWatch('read1', 'bar')
}

// XXX -- check if this is actually PR38762 before submitting upstream.

// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectWatchValue('bar', '0', '120000', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
