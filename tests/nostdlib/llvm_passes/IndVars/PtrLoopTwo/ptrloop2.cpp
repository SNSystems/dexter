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
  for (; ptr1 != &somearray[10]; ptr1++, ptr2++) {
  }

  return sum;
}

// Here, i becomes derived from an indvar, but no debug data is fixed,
// leading to it reporting '1' for all iterations.

// DexExpectWatchValue('i', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '1', '4', '9', '16', '36', '49', '64', '81', '100', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
