// RUN: %dexter
float foo[5];

int
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = 0, tmp2; // This huge block gets SLP vectorized,
  tmp1 = a1*(a1 + b1)/b1;
  tmp1 += 50*b1/a1;
  A[0] = tmp1;
  tmp1 = a2*(a2 + b2)/b2;
  tmp1 += 50*b2/a2;
  A[1] = tmp1;
  tmp2 = c1*(c1 + d1)/d1;
  tmp2 += 50*d1/c1;
  A[2] = tmp2;
  tmp1 = c2*(c2 + d2)/d2;
  tmp1 += 50*d2/c2;
  A[3] = tmp1;
  // From here, the code is scalar, and the tmp2 addition is an integer in
  // normal x86 registers. But because tmp2 comes from an slp vectorized
  // section of code, it doesn't get at dbg.value.
  tmp1 = a2*(a2 + d2)/d2;
  tmp1 += tmp2;     // DexWatch('tmp1', 'tmp2')
  tmp1 += 50*d2/a2; // DexWatch('tmp1', 'tmp2')
  A[4] = tmp1;      // DexWatch('tmp1', 'tmp2')
  return tmp2;      // DexWatch('tmp1', 'tmp2')
// DexExpectWatchValue('tmp1', '8', '66', '116')
// DexExpectWatchValue('tmp2', '58')
}

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  return bar(a1, a2, b1, b2, c1, c2, d1, d2, foo);
}

