// RUN: %dexter
float foo[4];

// Ensure that all arguments are readable after their usages are vectorized.
// Killing off args because their values are optimized would sucks.

void
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = a1*(a1 + b1)/b1; // DexWatch('a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 'A')
  tmp1 += 50*b1/a1;
  A[0] = tmp1;
  int tmp2 = a2*(a2 + b2)/b2;
  tmp2 += 50*b2/a2;
  A[1] = tmp2;
  int tmp3 = c1*(c1 + d1)/d1;
  tmp3 += 50*d1/c1;
  A[2] = tmp3;
  int tmp4 = c2*(c2 + d2)/d2;
  tmp4 += 50*d2/c2;
  A[3] = tmp4;
}

// DexExpectWatchValue('a1', '4')
// DexExpectWatchValue('a2', '4')
// DexExpectWatchValue('b1', '4')
// DexExpectWatchValue('b2', '4')
// DexExpectWatchValue('c1', '4')
// DexExpectWatchValue('c2', '4')
// DexExpectWatchValue('d1', '4')
// DexExpectWatchValue('d2', '4')

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  bar(a1, a2, b1, b2, c1, c2, d1, d2, foo);
  return foo[0];
}

