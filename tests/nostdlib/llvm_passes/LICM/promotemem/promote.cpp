// RUN: %dexter -- -fno-unroll-loops -fno-vectorize -fno-inline
// validation stats:
//  "licm.NumPromoted": 1,
//  "licm.NumSunk": 3,
// Loads and stores of *foop are promoted into being a load before the
// loop, and the store happening afterwards. The net effect being that
// the intermediate value lives in a register the whole time and trying to
// evaluate "*foop" during the middle of the loop gives you a stale value.
//
// Tested with -fno-unroll-loops -fno-vectorize -fno-inline

int foo = 0;

__attribute__((noinline))
static int
bar(int *foop)
{
  static int lolarray[4] = { 4, 4, 4, 4 }; // DexWatch('foo', 'lolarray', 'foop == &foo')

  for (int i = 0; i < 4; i++) {    // DexWatch('foo', '*foop', 'i', 'lolarray', 'foop == &foo')
    *foop += lolarray[i];          // DexWatch('foo', '*foop', 'i', 'lolarray', 'foop == &foo')
  }

  lolarray[3] = 0; // DexWatch('foo', '*foop', 'lolarray', 'foop == &foo')
  return *foop;    // DexWatch('foo', '*foop', 'lolarray', 'foop == &foo')
}

extern "C"
int
bounce()
{
  foo = 0;
  return bar(&foo);     // DexWatch('foo')
}

int
main()
{
  bounce();
}

// DexExpectWatchValue('i', '0', '1', '2', '3', from_line=1, to_line=50)
// DexExpectWatchValue('*foop',  '0', '4', '8', '12', '16', from_line=1, to_line=50)
// DexExpectWatchValue('foo',  '0', '4', '8', '12', '16', from_line=1, to_line=50)
// DexExpectWatchValue('lolarray',  '{4, 4, 4, 4}', '{4, 4, 4, 0}',  from_line=1, to_line=50)
// DexExpectWatchValue('foop == &foo', 'true', from_line=1, to_line=50)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexDiDi('*foop', ['4', '8', '12'], from_line=19, to_line=21)
// DexDiDi('foo', ['4', '8', '12'])
