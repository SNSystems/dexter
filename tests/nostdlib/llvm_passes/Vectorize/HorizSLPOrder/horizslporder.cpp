// RUN: %dexter
float
bar(float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2)
{
  float a = 0;
  float b = 0;
  float c = 0;
  float d = 0;
  float e = 0;
  float f = 0;
  float g = 0;
  a = a1 + a2; // DexWatch('a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2')
  b = b1 + b2;
  c = c1 + c2;
  d = d1 + d2;
  e = a + b;
  f = c + d;
  g = e + f;
  return g;
}

// DexExpectStepKind('BACKWARD', 0)
// DexExpectWatchValue('a1', '4')
// DexExpectWatchValue('a2', '4')
// DexExpectWatchValue('b1', '4')
// DexExpectWatchValue('b2', '4')
// DexExpectWatchValue('c1', '4')
// DexExpectWatchValue('c2', '4')
// DexExpectWatchValue('d1', '4')
// DexExpectWatchValue('d2', '4')
// Just ensure we don't step backwards for this func, also that args are
// readable

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  return (int)bar(a1, a2, b1, b2, c1, c2, d1, d2);
}

