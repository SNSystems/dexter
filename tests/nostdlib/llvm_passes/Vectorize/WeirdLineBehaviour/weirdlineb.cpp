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
  for (int j = 0; j < argc; j++) {// DexExpectStepOrder(1, 4, 7, 10, 13, 16, 19)
    tmp = init;
    tmp += j;                     // DexExpectStepOrder(2, 5, 8, 11, 14, 17, 20)
    bar[j] = tmp;                 // DexExpectStepOrder(3, 6, 9, 12, 15, 18, 21)
  }

  // Soooooo, this is another test where the line numbers bounce around quite
  // a bit in the VF=4 UF=16(?) loop. Instruction-level-parallelism may be
  // coming into play, but it's still freaky.

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
    return foo(74, 1);
  else
    return foo(atoi(argv[1]), 1);
}
