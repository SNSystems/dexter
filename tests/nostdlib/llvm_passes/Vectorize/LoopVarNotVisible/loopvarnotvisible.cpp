// RUN: %dexter
#include <stdlib.h>
#include <string.h>
#define BUFSZ 256

int
foo(int argc, int init)
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  if (argc + 1 > BUFSZ)
    return 0;

  memset(foo, 0, sizeof(foo));
  int tmp;
  for (int j = 0; j < argc; j++) { // DexWatch('tmp')
    tmp = init;                    // DexWatch('tmp')
    tmp += j;                      // DexWatch('tmp')
    bar[j] = tmp;                  // DexWatch('tmp')
  }

// DexExpectWatchValue('tmp', [])

// 'tmp' should be optimized out -- it never gets seen in this loop, because
// it's always vectorized. This happens to be the same for the scalar portion
// of it as well, but that could be changed.
// We swallow the 'optimized away' penalty from all the dexwatches, but don't
// assign any expected values. Thus, any value is unexpected, and a regression

  for (int i = 0; i < argc; i++)
    foo[i] += bar[i];

  int sum = 0;
  for (int i = 0; i < argc; i++)
    sum += foo[i];

  return sum;
}
#include <stdlib.h>

int foo(int argc, int init);

int
main(int argc, char **argv)
{
  if (argc == 1)
    return foo(8, 1);
  else
    return foo(atoi(argv[1]), 1);
}
