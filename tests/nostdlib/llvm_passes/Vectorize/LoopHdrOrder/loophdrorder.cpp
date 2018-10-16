// RUN: %dexter
#include <string.h>

#define BUFSZ 256

int
main(int argc, char **argv)
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  if (argc + 1 > BUFSZ)            // DexExpectStepOrder(1)
    return 0;

  memset(foo, 0, sizeof(foo));     // DexExpectStepOrder(2)
  for (int j = 0; j < argc; j++)   // DexExpectStepOrder(3, 5)
    bar[j] = 1;                    // DexExpectStepOrder(4)

  for (int i = 0; i < argc; i++)   // DexExpectStepOrder(6, 8)
    foo[i] += bar[i];              // DexExpectStepOrder(7)

  int sum = 0;
  for (int i = 0; i < argc; i++)   // DexExpectStepOrder(9, 11)
    sum += foo[i];                 // DexExpectStepOrder(10)

  return sum;                      // DexExpectStepOrder(12)
}

// For reasons unknown, at O2 there's a step back from the middle loop to the
// head of the first loop.
