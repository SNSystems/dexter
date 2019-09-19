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
  int sum = 0, other = 1;
  for (int i = 12; i < 22; i++, other++) {  // DexWatch('i', 'sum', 'other')
    sum += lul(i, other);                 // DexWatch('i', 'sum', 'other')
  }

  return sum;
}

// indvars ind-var's the iterator here, and calculates 'other' from it.
// However, it does this at the expense of deleting all debug values for
// other, leading to lots of 'optimised out's where they could be avoided
// Curiously if 'i' is declared out of the scope of the for loop, then the
// variable is optimised out too.

// DexExpectWatchValue('i', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '13', '28', '45', '64', '85', '108', '133', '160', '189', '220', from_line=1, to_line=50)
// DexExpectWatchValue('other', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
