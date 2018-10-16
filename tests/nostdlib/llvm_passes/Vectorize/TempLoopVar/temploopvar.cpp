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
  int tmp = 12;
  for (int j = 0; j < argc; j++) { // DexWatch('tmp')
    tmp = init;  // DexUnreachable()
    tmp += argc; // DexUnreachable()
    bar[j] = tmp;// DexWatch('tmp')
  }

// DexExpectWatchValue('tmp', '12', '75')
// Tmp gets hoisted; check that this behaviour doesn't change. Mark
// intermediate lines as unreachable -- if they become reachable, this test
// needs to change.
// Really doesn't work with O0.

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
    return foo(74, 1); // 64 + 8 + 2 = round each unrolling of vectorization
  else
    return foo(atoi(argv[1]), 1);
}
