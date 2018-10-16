// RUN: %dexter
#include <string.h>
#define BUFSZ 256

int foo[BUFSZ];
int
main(int argc, char **argv) // DexWatch('argc')
{
  if (argc + 1 > BUFSZ)     // DexWatch('argc')
    return 0;

  memset(foo, 0, argc * sizeof(int)); // DexWatch('argc')

  return foo[argc / 2];     // DexWatch('argc')
}

// Found during vectorization stuff but not specific to vectors: the
// locations of argc and argv get corrupted and assigned to an uninitialized
// variable, for some reason.
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38952

// DexExpectWatchValue('argc', '1')
