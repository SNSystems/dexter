// RUN: %dexter
#include <stdlib.h>
#include <string.h>

#define BUFSZ 256

int
foo(int argc)
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  if (argc + 1 > BUFSZ)
    return 0;

  // So: when fed '8' as the loop size (argc), we step in and out of the loop
  // below three times, but only on 'bar[j] += argc' once. It's a pain if
  // you have an expectation about the loop having the same body on each
  // iteration of the loop; and in fact, this _does_ exercise the same (VF=4
  // UF=2) body each time. It's just that the surrounding plumbing encodes
  // a few steps through the loop of its own account.
  // If you run with argc==10, you get each flavour of the loop, the first line
  // by itself, then both, then only the last line.
  // This test just doesn't work well in -O0

  memset(foo, 0, sizeof(foo));
  for (int j = 0; j < argc; j++) { // DexExpectStepOrder(1, 4, 7)
    bar[j] = 1;                    // DexExpectStepOrder(2, 5, 8)
    bar[j] += argc;                // DexExpectStepOrder(3, 5, 9)
  }

  for (int i = 0; i < argc; i++)
    foo[i] += bar[i];

  int sum = 0;
  for (int i = 0; i < argc; i++)
    sum += foo[i];

  return sum;
}

#include <stdlib.h>

int foo(int argc);

int
main(int argc, char **argv)
{
  if (argc == 1)
    return foo(8);
  else
    return foo(atoi(argv[1]));
}
