// RUN: %dexter
float foo[5];

void
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2, float *A)
{
  int tmp1 = 0;
  tmp1 = a1*(a1 + b1)/b1; // DexExpectStepOrder(1)
  tmp1 += 50*b1/a1; // DexExpectStepOrder(2)
  A[0] = tmp1; // DexExpectStepOrder(3)
  tmp1 = a2*(a2 + b2)/b2; // DexExpectStepOrder(4)
  tmp1 += 50*b2/a2; // DexExpectStepOrder(5)
  A[1] = tmp1; // DexExpectStepOrder(6)
  if (a1 == 4) { // DexExpectStepOrder(7)
    tmp1 = c1*(c1 + d1)/d1; // DexExpectStepOrder(8)
    tmp1 += 50*d1/c1; // DexExpectStepOrder(9)
    A[2] = tmp1; // DexExpectStepOrder(10)
  }
  tmp1 = c2*(c2 + d2)/d2; // DexExpectStepOrder(11)
  tmp1 += 50*d2/c2; // DexExpectStepOrder(12)
  A[3] = tmp1; // DexExpectStepOrder(13)
  tmp1 = a2*(a2 + d2)/d2; // DexExpectStepOrder(14)
  tmp1 += 50*d2/a2; // DexExpectStepOrder(15)
  A[4] = tmp1; // DexExpectStepOrder(16)
}

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  bar(a1, a2, b1, b2, c1, c2, d1, d2, foo);
  return 0;
}

