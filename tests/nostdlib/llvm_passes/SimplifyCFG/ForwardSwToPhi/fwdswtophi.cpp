// RUN: %dexter
int
main()
{
  volatile int foo = 4;  // DexExpectStepOrder(1)
  int read1 = foo;       // DexExpectStepOrder(2)

  int bar = 0;
  switch (read1) {       // DexExpectStepOrder(3)
  case 0:    // DexUnreachable()
    bar = 3; // DexUnreachable()
    break;   // DexUnreachable()
  case 12:   // DexUnreachable()
    bar = 15;// DexUnreachable()
    break;   // DexUnreachable()
  case 1256: // DexUnreachable()
    bar = 854;// DexUnreachable()
    break;   // DexUnreachable()
  case 30:
  default:
    bar = 1;    // DexExpectStepOrder(4)
  }

  return bar; // DexExpectStepOrder(5)
}

// This is another case where at O2, the structure of the program (is
// transformed but) stays the same enough that we should see the
// assignment of 1 to bar. But don't.

// DexExpectStepKind('VERTICAL_BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
