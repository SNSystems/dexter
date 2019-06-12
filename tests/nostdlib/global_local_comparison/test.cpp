// RUN: %dexter

int a = 1;
int b = 2;

int main()
{
  int c = a; // DexWatch('a', 'b')
  int d = b; // DexWatch('a', 'b', 'c')

  if (d != c)  // DexWatch('a', 'b', 'c', 'd')
    return -1;

  return 0;
}

// DexExpectWatchValue('a', '1')
// DexExpectWatchValue('b', '2')
// DexExpectWatchValue('c', '1')
// DexExpectWatchValue('d', '2')
