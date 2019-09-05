// RUN: %dexter -- -fno-unroll-loops
int
lul(int i, int other)
{
  volatile int foo = i;
  return foo + other;
}

int
main()
{
  int sum = 0;
  for (int i = 12; i < 22; i++) {  // DexWatch('i', 'sum')
    bool isend = i >= 22;
    sum += lul(i, (isend) ? 1 : 0);          // DexWatch('i', 'sum', 'isend')
  }

  return sum;  // DexWatch('sum')
}

// indvars can tell that isend is always false here, but doesn't bother to
// record the relevant debug data. It does if you change the polarity of the
// test though.

// DexExpectWatchValue('i', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '12', '25', '39', '54', '70', '87', '105', '124', '144', '165', from_line=1, to_line=50)
// DexExpectWatchValue('isend', 'false', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
