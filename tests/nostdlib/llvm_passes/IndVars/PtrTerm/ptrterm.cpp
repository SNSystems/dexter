// RUN: %dexter -- -fno-unroll-loops
int
lul(int i, int other)
{
  volatile int foo = i;
  return foo + other;
}

int
somearray[] = {
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 };

int
main()
{
  int sum = 0;
  int *ptr1 = &somearray[0];
  int *ptr2 = &somearray[1];
  int i = 0;
  for (i = 0; i < 10; i++, ptr1++, ptr2++) {
    sum += lul(*ptr1, *ptr2);
  }

  i += *ptr1; // DexWatch('ptr1', 'ptr2')
  i += *ptr2; // DexWatch('ptr1', 'ptr2')
  sum += i;   // DexWatch('i', 'sum')

  return sum;  // DexWatch('sum')
}

// LLVM knows where ptr1 and ptr2 point at the end of the loop (it issues
// a pcrel access for one), but we can't print their values. Don't watch
// for value in test, just dexwatch the variable and eat the optimised-out
// penalty.

// DexExpectWatchValue('i', '31', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '100', '131', from_line=1, to_line=50)
// DexExpectStepKind('VERTICAL_BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
