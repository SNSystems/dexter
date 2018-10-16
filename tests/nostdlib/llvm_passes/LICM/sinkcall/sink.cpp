// RUN: %dexter
// validation stats:
//  "licm.NumMovedCalls": 1,
//  "licm.NumSunk": 1,
// Call to set "extra" with "getrandvar" is sunk to end of loop
static int inorder[] = { 0, 1, 2, 3, 4 };
static int randvars[] = { 4, 4, 4, 4, 4 };

__attribute__((noinline))
static int
getinorder(int idx)
{
  return inorder[idx];
}

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
  int extra = 0;                   // DexWatch('sum')
  for (int i = 0; i < 4; i++) {    // DexWatch('sum', 'extra')
    sum += getrandvar(i);          // DexWatch('sum', 'extra', 'i')
    extra = getinorder(i);         // DexWatch('sum', 'extra', 'i')
    sum %= 4;                      // DexWatch('sum', 'extra', 'i')
  }
  return sum + extra;              // DexWatch('sum', 'extra')
}

int
main()
{
  return bounce();
}

// DexExpectWatchValue('i', '0', '1', '2', '3', from_line=28, to_line=32)
// DexExpectWatchValue('sum',  '0', '4', '0', '4', '0', '4', '0', '4', '0', from_line=27, to_line=34)
// DexExpectWatchValue('extra', '0', '1', '2', '3', from_line=28, to_line=34)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
