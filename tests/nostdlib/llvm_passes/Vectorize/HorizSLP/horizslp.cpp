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
  a = a1 + a2; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g') 
  b = b1 + b2; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  c = c1 + c2; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  d = d1 + d2; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  e = a + b; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  f = c + d; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  g = e + f; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
  return g; // DexWatch('a', 'b', 'c', 'd', 'e', 'f', 'g')
}

// DexExpectWatchValue('a', 0)
// DexExpectWatchValue('b', 0)
// DexExpectWatchValue('c', 0)
// DexExpectWatchValue('d', 0)
// DexExpectWatchValue('e', 0)
// DexExpectWatchValue('f', 0)
// DexExpectWatchValue('g', 0, 32)

// We shouldn't see any intermediate values when horizontally vectorized
// This doesn't work at all with -O0
// Scoring is interesting in that we get -7 for values that were partially
// seen?

int
main() {
  volatile float a1, a2, b1, b2, c1, c2, d1, d2;
  a1 = a2 = b1 = b2 = c1 = c2 = d1 = d2 = 4;

  return (int)bar(a1, a2, b1, b2, c1, c2, d1, d2);
}

