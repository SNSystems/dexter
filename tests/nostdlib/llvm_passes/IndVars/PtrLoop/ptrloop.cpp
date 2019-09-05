// RUN: %dexter -- -fno-unroll-loops
int
lul(int i, int other)
{
  volatile int foo = i;
  return foo + other;
}

int
somearray[] = {
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

int
main()
{
  int sum = 0;
  int *ptr = somearray;
  for (int i = 1; i < 11; i++, ptr++) { // DexWatch('i', 'sum')
    sum += lul(i, *ptr);                // DexWatch('i', 'sum')
  }

  return sum;  // DexWatch('sum')
}

// Here, i becomes derived from an indvar, but no debug data is fixed,
// leading to it reporting '1' for all iterations.
// And inexplicably 'sum' gets const-zero'd, on some lines, not others!
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38779

// DexExpectWatchValue('i', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '1', '4', '9', '16', '25', '36', '49', '64', '81', '100', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
