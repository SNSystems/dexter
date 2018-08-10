int Foo(const int iterations, const int initial)
{
  static int val = initial; // DexWatch('iterations', 'initial')

  for (static int i = 0; i <= iterations; ++i)
    val += (i % 2 ? 50 : 25) * i; // DexWatch('iterations', 'val', 'i')

  return val; // DexWatch('val')
}

// DexExpectWatchValue('iterations', '5', on_line=3)
// DexExpectWatchValue('initial', '6', on_line=3)

// DexExpectWatchValue('iterations', '5', on_line=6)
// DexExpectWatchValue('i', '0', '1', '2', '3', '4', '5', on_line=6)
// DexExpectWatchValue('val', '6', '56', '106', '256', '356', on_line=6)

// DexExpectWatchValue('val', '606', on_line=8)
