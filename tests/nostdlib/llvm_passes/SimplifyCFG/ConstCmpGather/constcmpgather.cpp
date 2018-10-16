// RUN: %dexter
#include <stdio.h>

// This gets threaded into being a switch; should have very little effect on
// debuggability

int
look(int val, int pony, int *nou) // DexWatch('val', 'pony', '*nou')
{
  int frob = 0;             // DexWatch('val', 'pony', '*nou', 'frob', 'out')
  int out = 0;              // DexWatch('val', 'pony', '*nou', 'frob', 'out')
  if (val < 3 && val > 1) {
    out = 0;
    frob = val * pony;
  } else if (val > 0 && val < 2) {
    out = 1;
    frob = val + pony;
  } else if (val > -1 && val < 1) {
    out = 2;                // DexWatch('val', 'pony', '*nou', 'frob', 'out')
    frob = val - pony;      // DexWatch('val', 'pony', '*nou', 'frob', 'out')
  } else if (val > 2 && val < 4) {
    out = 3;
    frob = val / pony;
  } else {
    out = 4;
    frob = *nou;
  }
  printf("clobber\n");  // DexWatch('val', 'pony', '*nou', 'frob', 'out')
  *nou = frob;          // DexWatch('val', 'pony', '*nou', 'frob', 'out')
  return out;           // DexWatch('val', 'pony', '*nou', 'frob', 'out')
}

int
main()
{
  volatile int beards = 0;
  volatile int trains = 4;
  int nou = 0;
  int fgasdf = look(beards, trains, &nou); // DexWatch('nou')
  return fgasdf + nou;  // DexWatch('fgasdf', 'nou')
}

// DexExpectWatchValue('nou', '0', '-4', from_line=1, to_line=50)
// DexExpectWatchValue('fgasdf', '2', from_line=1, to_line=50)
// DexExpectWatchValue('val', '0', from_line=1, to_line=50)
// DexExpectWatchValue('pony', '4', from_line=1, to_line=50)
// DexExpectWatchValue('*nou', '0', '-4', from_line=1, to_line=50)
// DexExpectWatchValue('frob', '0', '-4', from_line=1, to_line=50)
// DexExpectWatchValue('out', '0', '2', from_line=1, to_line=50)

// The printf...
// DexExpectStepKind('FUNC_EXTERNAL', 1)
// DexExpectStepKind('BACKWARD', 0)
