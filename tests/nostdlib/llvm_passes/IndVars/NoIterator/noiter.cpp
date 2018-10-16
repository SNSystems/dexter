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
  for (i = 0; i < 10; i++, ptr1++, ptr2++) { // DexWatch('i', 'sum')
    sum += lul(*ptr1, *ptr2);                // DexWatch('i', 'sum')
  }

  i *= 20;   // DexWatch('i', 'sum')
  i /= 3;    // DexWatch('i', 'sum')
  sum += i;  // DexWatch('i', 'sum')

  return sum;  // DexWatch('sum')
}

// 'i' is the induction variable here, and its exit value can be accurately
// predicted. As a result llvm will constprop up to the addition to sum.
// All the intervening dbg.value's get deleted, so you can't tell where in
// the loops iterations you are.
// Better, the value of 'i' isn't accessible at the start or end of the loop
// from the gdb command line interface, nor the lldb one, but somehow dexter
// manages to observe i == 66. The debug record is there in dwarfdump, but
// with a zero-width interval.

// DexExpectWatchValue('i', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '200', '66', from_line=1, to_line=50)
// DexExpectWatchValue('sum', '0', '1', '4', '9', '16', '25', '36', '49', '64', '81', '100', '166', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 10)
// DexExpectStepKind('FUNC', 21)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
