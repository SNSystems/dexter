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
    sum += lul(*ptr1, *ptr2); // DexExpectStepOrder(1, 3, 5, 7, 9, 11)
    if (i > 4)                // DexExpectStepOrder(2, 4, 6, 8, 10, 12)
      break;
  }

  i += *ptr1;
  i += *ptr2;
  sum += i;

  return sum;
}

// With *gdb*, each loop iteration (save the first) only features the if
// condition, which is deeply misleading.
// Not clear if this is LLVM or GDB though, because lldb seems to do ok

// DexExpectStepKind('BACKWARD', 5)
// DexExpectStepKind('FUNC', 13)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
