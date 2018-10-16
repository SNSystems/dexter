// RUN: %dexter -- -fno-unroll-loops
// Notes: needs to be compiled -fno-unroll-loops
// Need to check that stats results has '"licm.NumHoisted": 2'
int randvars[] = { 4, 4, 4, 4 };

__attribute__((noinline))
static int
getrandvar(int idx)
{
  return randvars[idx];
}

static int
foo()
{
  int sum = 0;
  int other = getrandvar(0);       // DexWatch('sum')
  for (int i = 0; i < 4; i++) {    // DexWatch('sum', 'other')
    int hoist1 = other * 3;        // DexWatch('sum', 'other', 'i')
    int hoist2 = hoist1 + 14;      // DexWatch('sum', 'other', 'i', 'hoist1')
    sum += getrandvar(i);          // DexWatch('sum', 'other', 'i', 'hoist1', 'hoist2')
    sum %= hoist2;                 // DexWatch('sum', 'other', 'i', 'hoist1', 'hoist2')
  }
  return sum;                      // DexWatch('sum', 'other')
}

extern "C"
int
bounce()
{
  return foo();
}

int
main()
{
  return bounce();
}

// DexExpectWatchValue('i', '0', '1', '2', '3', from_line=19, to_line=23)
// DexExpectWatchValue('sum',  '0', '4', '8', '12', '16', from_line=17, to_line=24)
// DexExpectWatchValue('other', '4', from_line=18, to_line=24)
// DexExpectWatchValue('hoist1', '12', from_line=20, to_line=23)
// DexExpectWatchValue('hoist2', '26', from_line=21, to_line=23)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
