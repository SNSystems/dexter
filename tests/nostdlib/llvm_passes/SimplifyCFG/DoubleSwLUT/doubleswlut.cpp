// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;

  int bar = 0;
  int baz = 1;
  switch (read1) {     // DexExpectStepOrder(1)
  case 0:              // DexUnreachable()
    bar = read1 * 2;   // DexUnreachable()
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
  case 4:
    bar = read1 + 22; // DexExpectStepOrder(2)
    baz = 2;
    break;
  case 5:             // DexUnreachable()
    bar = read1 - 100;// DexUnreachable()
    break;            // DexUnreachable()
  case 6:             // DexUnreachable()
    bar = read1 * 3000;// DexUnreachable()
    break;            // DexUnreachable()
  case 7:             // DexUnreachable()
    bar = read1 | 777;// DexUnreachable()
    break;            // DexUnreachable()
  }

  return bar + baz; // DexExpectStepOrder(3)
}

// Due to the assignment to baz in the switch, this switch becomes not one
// but _two_ LUTs. Test for running over the live lines (which we expect to
// get optimized out).

// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
