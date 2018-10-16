// RUN: %dexter
int
main()
{
  volatile int foo = 8;
  int read1 = foo;

  int bar = 0;
  int baz = 1;
  switch (read1) {     // DexExpectStepOrder(1)
  case 0:              // DexUnreachable()
    bar = read1 + 8;   // DexUnreachable()
    break;             // DexUnreachable()
  case 1:              // DexUnreachable()
    bar = read1 + 2;   // DexUnreachable()
    break;             // DexUnreachable()
  case 2:              // DexUnreachable()
    bar = read1 / 3;   // DexUnreachable()
    break;             // DexUnreachable()
  case 3:              // DexUnreachable()
    bar = read1 & 3;   // DexUnreachable()
    break;             // DexUnreachable()
  case 4:              // DexUnreachable()
    bar = read1 + 22;  // DexUnreachable()
    baz = 2;           // DexUnreachable()
    break;             // DexUnreachable()
  case 5:              // DexUnreachable()
    bar = read1 - 100; // DexUnreachable()
    break;             // DexUnreachable()
  case 6:              // DexUnreachable()
    bar = read1 * 3000;// DexUnreachable()
    break;             // DexUnreachable()
  case 7:              // DexUnreachable()
    bar = read1 | 777; // DexUnreachable()
    break;             // DexUnreachable()
  default:
    bar = 0;
    break;
  }

  if (bar == 0)
    baz = 12;  // DexExpectStepOrder(2)

  return bar + baz; // DexExpectStepOrder(3)
}

// SimplifyCFG merges 'baz = 12' into the default path as it can statically
// detect its unconditional execution. But, we still don't see the line
// numbers for some reason.

// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
