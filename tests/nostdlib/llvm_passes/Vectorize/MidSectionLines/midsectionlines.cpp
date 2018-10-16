#include <stdlib.h>
#include <string.h>

#define BUFSZ 256

int
foo(int argc, int init, int *bar)
{

  if (argc + 1 > BUFSZ)
    return 0;

  int tmp = argc;
  int bees;
  for (int j = 0; j < argc; j++) {
    bees = bar[j];
    if (j & 1) {
      bees += init;
      tmp += 1;
    }
    bar[j] = bees;
    tmp += 3;
  }

  return tmp;
}

// See associated README file
// Reported: https://bugs.llvm.org/show_bug.cgi?id=39024
#include <stdlib.h>

int foo(int argc, int init, int *bar);

int
main(int argc, char **argv)
{
  int bar[256];
  if (argc == 1)
    return foo(16, 1, bar);
  else
    return foo(atoi(argv[1]), 1, bar);
}
