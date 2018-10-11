int
main()
{
  volatile int foo = 4;//DexWatch('foo')
  int read1 = foo;     // DexExpectStepOrder(1)

  // The below is common'd out with O2
  if (read1 == 5) {    // DexExpectStepOrder(2)
    return 8;
  } else if (read1 == 4) {
    return 1200000;    // DexExpectStepOrder(3)
  } else if (read1 == 60) {
    return 3;
  } else {
    return -1;
  }
} // DexExpectStepOrder(4)
