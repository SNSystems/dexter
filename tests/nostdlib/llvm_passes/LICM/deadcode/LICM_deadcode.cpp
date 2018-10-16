// RUN: %dexter
// Need to check that stats results has '"licm.NumHoisted": 2'
// NB, the idea here is that hoist2 isn't used and thus we should score
// _less_ than LICM_hoist, because it's going to be optimized out all the
// time.
// XXX XXX XXX -- licm doesn't seem to delete hoist2, something else does.
static int randvars[] = { 4, 4, 4, 4 };

__attribute__((noinline))
static int
getrandvar(int idx)
{
  return randvars[idx];
}

extern "C" int
bounce()
{
  int sum = 0;
  int other = getrandvar(0);       // DexWatch('sum')
  for (int i = 0; i < 4; i++) {    // DexWatch('sum', 'other')
    int hoist1 = other * 3;        // DexWatch('sum', 'other', 'i')
    int hoist2 = hoist1 + 14;      // DexWatch('sum', 'other', 'i', 'hoist1')
    sum += getrandvar(i);          // DexWatch('sum', 'other', 'i', 'hoist1', 'hoist2')
    sum %= hoist1;                 // DexWatch('sum', 'other', 'i', 'hoist1', 'hoist2')
  }
  return sum;                      // DexWatch('sum', 'other')
}

int
main()
{
  return bounce();
}

// DexExpectWatchValue('i', '0', '1', '2', '3', from_line=1, to_line=50)
// DexExpectWatchValue('sum',  '0', '4', '8', '12', '0', '4', from_line=1, to_line=50)
// DexExpectWatchValue('other', '4', from_line=1, to_line=50)
// DexExpectWatchValue('hoist1', '12', from_line=1, to_line=50)
// DexExpectWatchValue('hoist2', '26', from_line=1, to_line=50)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
