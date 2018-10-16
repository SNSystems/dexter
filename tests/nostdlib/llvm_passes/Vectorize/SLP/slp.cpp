// RUN: %dexter
float foo[4];

void
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = a1*(a1 + b1)/b1; // DexWatch('A', 'tmp1')
  tmp1 += 50*b1/a1;           // DexWatch('A', 'tmp1')
  A[0] = tmp1;                // DexWatch('A', 'tmp1')
  int tmp2 = a2*(a2 + b2)/b2; // DexWatch('A', 'tmp1', 'tmp2')
  tmp2 += 50*b2/a2;           // DexWatch('A', 'tmp1', 'tmp2')
  A[1] = tmp2;                // DexWatch('A', 'tmp1', 'tmp2')
  int tmp3 = c1*(c1 + d1)/d1; // DexWatch('A', 'tmp1', 'tmp2', 'tmp3')
  tmp3 += 50*d1/c1;           // DexWatch('A', 'tmp1', 'tmp2', 'tmp3')
  A[2] = tmp3;                // DexWatch('A', 'tmp1', 'tmp2', 'tmp3')
  int tmp4 = c2*(c2 + d2)/d2; // DexWatch('A', 'tmp1', 'tmp2', 'tmp3', 'tmp4')
  tmp4 += 50*d2/c2;           // DexWatch('A', 'tmp1', 'tmp2', 'tmp3', 'tmp4')
  A[3] = tmp4;                // DexWatch('A', 'tmp1', 'tmp2', 'tmp3', 'tmp4')
}

// Check that when SLP vectorized, the designated variables are unreadable.
// There's no expect-value checker, thus any value read is reported as an error
// (I think)

void
baz(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = a1*(a1 + b1)/b1;
  tmp1 += 50*b1/a1;
  A[0] = tmp1;
  int tmp2 = a2*(a2 + b2)/b2;   // DexUnreachable()
  tmp2 += 50*b2/a2;             // DexUnreachable()
  A[1] = tmp2;                  // DexUnreachable()
  int tmp3 = c1*(c1 + d1)/d1;   // DexUnreachable()
  tmp3 += 50*d1/c1;             // DexUnreachable()
  A[2] = tmp3;                  // DexUnreachable()
  int tmp4 = c2*(c2 + d2)/d2;   // DexUnreachable()
  tmp4 += 50*d2/c2;             // DexUnreachable()
  A[3] = tmp4;                  // DexUnreachable()
}
// Check that when SLP vectorized, we don't step through random bits of the
// vectorized function. This *might* be fragile wrt. where the vectorizer
// picks its DebugLocs from, but it's not clear whether that's liable to change


int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  bar(a1, a2, b1, b2, c1, c2, d1, d2, foo);
  baz(a1, a2, b1, b2, c1, c2, d1, d2, foo);
  return 0;
}

