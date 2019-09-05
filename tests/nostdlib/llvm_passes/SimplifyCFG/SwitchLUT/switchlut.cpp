// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;

  int bar = 0;
  switch (read1) { // DexExpectStepOrder(1)
  case 0:          // DexUnreachable()
    bar = -100;    // DexUnreachable()
    break;         // DexUnreachable()
  case 1:          // DexUnreachable()
    bar = 0;       // DexUnreachable()
    break;         // DexUnreachable()
  case 2:          // DexUnreachable()
    bar = 106;     // DexUnreachable()
    break;         // DexUnreachable()
  case 3:          // DexUnreachable()
    bar = 209;     // DexUnreachable()
    break;         // DexUnreachable()
  case 4:
    bar = 303;     // DexExpectStepOrder(2)
    break;
  case 5:          // DexUnreachable()
    bar = 408;     // DexUnreachable()
    break;         // DexUnreachable()
  case 6:          // DexUnreachable()
    bar = 503;     // DexUnreachable()
    break;         // DexUnreachable()
  case 7:          // DexUnreachable()
    bar = 601;     // DexUnreachable()
    break;         // DexUnreachable()
  }

  return bar;  // DexWatch('bar')
}

// The above switch is optimised to a lookup table for O2, and as a result
// we don't get to see the assignment of bar = 303. We should get to see
// the return value though

// DexExpectWatchValue('bar', '303', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
