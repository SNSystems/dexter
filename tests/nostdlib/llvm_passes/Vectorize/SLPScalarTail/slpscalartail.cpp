// RUN: %dexter
float foo[5];

void
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = 0;
  tmp1 = a1*(a1 + b1)/b1;
  tmp1 += 50*b1/a1;
  A[0] = tmp1;
  tmp1 = a2*(a2 + b2)/b2;
  tmp1 += 50*b2/a2;
  A[1] = tmp1;
  tmp1 = c1*(c1 + d1)/d1;
  tmp1 += 50*d1/c1;
  A[2] = tmp1;
  tmp1 = c2*(c2 + d2)/d2;
  tmp1 += 50*d2/c2;
  A[3] = tmp1;
  tmp1 = a2*(a2 + d2)/d2; // DexWatch('a2', 'd2')
  tmp1 += 50*d2/a2; // DexWatch('tmp1', 'a2', 'd2')
  A[4] = tmp1;      // DexWatch('tmp1')
}

// Scalar tail of this loop should be visible
// DexExpectWatchValue('a2', '4')
// DexExpectWatchValue('d2', '4')
// DexExpectWatchValue('tmp1', '8', '58')

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  bar(a1, a2, b1, b2, c1, c2, d1, d2, foo);
  return 0;
}

