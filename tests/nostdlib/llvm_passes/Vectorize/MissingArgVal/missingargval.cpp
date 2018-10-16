// RUN: %dexter
#include <string.h>

#define BUFSZ 256

int
main(int argc, char **argv) // DexWatch('argc')
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  if (argc + 1 > BUFSZ) // DexWatch('argc')
    return 0; // DexUnreachable()

  memset(foo, 0, sizeof(foo)); // DexWatch('argc')
  memset(bar, 1, sizeof(bar)); // DexWatch('argc')

  for (int i = 0; i < argc; i++) // DexWatch('argc')
    foo[i] += bar[i]; // DexWatch('argc')

  int sum = 0; // DexWatch('argc')
  for (int i = 0; i < argc; i++) // DexWatch('argc')
    sum += foo[i]; // DexWatch('argc')

  return sum; // DexWatch('argc')
}

// We inexplicably get argc highly wrong in the prologue, and invisible
// through the rest of it

// DexExpectWatchValue('argc', '1')
