// RUN: %dexter
#include <string.h>

#define BUFSZ 32

int
main()
{
  int foo[BUFSZ];
  int bar[BUFSZ];

  memset(foo, 0, sizeof(foo));
  for (int i = 0; i < BUFSZ; i++)
    bar[i] = 1;

  for (int i = 0; i < BUFSZ; i++)
    foo[i] += bar[i];

  int sum = 0; // DexWatch('sum')
  for (int i = 0; i < BUFSZ; i++) // DexWatch('sum')
    sum += foo[i]; // DexWatch('sum')

  return sum; // DexWatch('sum')
}

// Tricky: these loops get vectorised, _and_ unrolled, to make zero loops.
// This is fine; however the value of 'sum' is not available at the end of
// the loop for some reason, _despite_ the fact it's in $rax, which is
// annoying
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=39019

// DexExpectWatchValue('sum', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32')
// DexExpectStepKind('FUNC', 1)
// In theory the memsets are external funcs, in practice they get localised
// DexExpectStepKind('FUNC_EXTERNAL', 0)
