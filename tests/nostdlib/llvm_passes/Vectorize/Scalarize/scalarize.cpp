// RUN: %dexter
#include <stdlib.h>
#include <string.h>

#define BUFSZ 16

void
xyzzy(int ** out, int len)
{
#pragma clang loop vectorize(enable) vectorize_width(4) interleave_count(1)
  for (int i = 0; i < len; i++) { // DexWatch('len')
    int tmp = i;
    tmp += len;    // DexWatch('len', 'tmp')
    tmp += 12;     // DexWatch('len', 'tmp')
    *out[i] = tmp; // DexWatch('len', 'tmp')
  }
// Gratuitously vectorize a loop and then scalarize it's writeback, just to
// see if 'tmp' gets values reported. (It doesn't). 'i' is currently constant
// zero on account of other bugs.
// DexExpectWatchValue('len', '16')
// No watch value for tmp -> max penalty if a value is seen.
}

void
xyzzy2(int ** out, int len)
{
#pragma clang loop vectorize(enable) vectorize_width(4) interleave_count(1)
  for (int i = 0; i < len; i++) { // DexExpectStepOrder(1, 4, 7, 10)
    int tmp = i;
    tmp += len;
    tmp += 12;     // DexExpectStepOrder(2, 5, 8, 11)
    *out[i] = tmp; // DexExpectStepOrder(3, 6, 9, 12)
  }
// Gratuitously vectorize a loop and check stepping: the writebacks to out
// are (excellently) all in one block, but there's then a jump back to
// '+= 12' where it would appear the induction-incrementing of 'i' in a vector
// register gets the wrong line no? Either way, generates a spurious step.
}

int
main()
{
  int baz[BUFSZ];
  int *qux[BUFSZ];

  for (int i = 0; i < BUFSZ; i++) {
    qux[i] = &baz[i];
  }

  xyzzy(qux, BUFSZ);
  xyzzy2(qux, BUFSZ);
  return baz[0];
}
