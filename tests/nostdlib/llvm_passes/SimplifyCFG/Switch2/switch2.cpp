// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read1 = foo;    // DexExpectStepOrder(1)
  int read2 = foo;    // DexExpectStepOrder(2)

  int bar = 0;
  switch (read1) {    // DexExpectStepOrder(3)
  case 0:
    bar = 16 * read2; // DexUnreachable()
    bar += 7;         // DexUnreachable()
    break;            // DexUnreachable()
  default:
    bar = 120000;     // DexExpectStepOrder(4)
  }

  return bar;         // DexExpectStepOrder(5)
}

// This test likely replicates upstream PR38762, just via the medium of
// switches.
