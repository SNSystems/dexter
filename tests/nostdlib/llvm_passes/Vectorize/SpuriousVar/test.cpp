// In this file, the 'bees' variables first assignment in the loop gets
// hoisted out, and the rest of the pipeline decides that it's live across
// the vectorized loop. This leads to the _good_ debug feature of the variable
// having a location on the line using the hoisted value (which would
// otherwise be unavailable), but the bad debug feature of it being the wrong
// value for the rest of the loop.
// The actual bug here is a repeat of LLVM PR39018
#include <stdlib.h>
#include <string.h>
#include <stdlib.h>

#define BUFSZ 256

int
foo(int argc, int init)
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  if (argc + 1 > BUFSZ)
    return 0;

  memset(foo, 0, sizeof(foo));
  memset(bar, 0, sizeof(bar));
  int tmp = argc;
  int bees = 0;
  for (int j = 0; j < argc; j++) {
    bees = tmp + init;
    bees += bar[j];
    if (j & 1)
      bees += 1;
    bar[j] = bees;
  }

  for (int i = 0; i < argc; i++)
    foo[i] += bar[i];

  int sum = 0;
  for (int i = 0; i < argc; i++)
    sum += foo[i];

  return sum;
}

int
main(int argc, char **argv)
{
  if (argc == 1)
    return foo(8, 1);
  else
    return foo(atoi(argv[1]), 1);
}
