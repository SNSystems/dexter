// RUN: %dexter -- -fno-unroll-loops
int
lul(int i)
{
  volatile int foo = i;
  return foo;
}

int
main()
{
  int sum = 0, i = 12;
  for (i = 12; i < 22; i++) {  // DexWatch('i', 'sum')
    sum += lul(i);                 // DexWatch('i', 'sum')
  }

  return sum;
}

// All indvars does to this (without funroll loops) is reduce the exit
// condition strength.

// DexExpectWatchValue('i', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '12', '25', '39', '54', '70', '87', '105', '124', '144', '165', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
