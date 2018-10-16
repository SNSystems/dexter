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
  int tmp = argc;;
  for (int j = 0; j < argc; j++) {
    int bees = bar[j];
    if (j & 1)
      bees += init; // DexUnreachable()
// Slightly more sophisticated unreachable test
    bar[j] = bees;
    tmp -= 1;
  }

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
