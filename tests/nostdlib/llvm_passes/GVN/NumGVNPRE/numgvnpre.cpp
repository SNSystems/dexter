// RUN: %dexter
int g0 = 0, g1 = 0, g2 = 0;
int
baz(int *p0, int *p1, int *p2)
{
  int accuml = 0, inbranch = 0, extra = 0;

  // GVN should hoist the calculations for accuml into the false branch,
  // where it promptly messes witht he program flow.
  int preload0 = *p0;
  int preload1 = *p1;
  int preload2 = *p2;
  if (*p0) {                      // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    inbranch += preload0 + 1;     // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    inbranch *= preload2;         // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    inbranch /= preload1;         // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    inbranch += 12;               // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    extra += preload0 + 1;        // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
  } else {                        // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    inbranch = preload2 + 18;     // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
    extra += preload1 + 2;        // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
  }                               // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')

  extra += 4;                     // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')

  accuml += preload0 + 1;         // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
  accuml *= preload2;             // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
  accuml /= preload1;             // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
  return accuml + inbranch + extra; // DexWatch('inbranch', 'accuml', 'extra', 'g0', 'g1', 'g2')
}

// XXX -- with clang 6.0 'accuml /= preload1' appears hoisted into the branch,
// with the value of 'accuml' as zero, which is illegal. But Dexter won't detect
// that by default?

int
main()
{
  volatile int zero = 0;
  volatile int one = 1;
  volatile int two = 2;
  g0 = zero; // DexWatch('g0', 'g1', 'g2')
  g1 = one;  // DexWatch('g0', 'g1', 'g2')
  g2 = two;  // DexWatch('g0', 'g1', 'g2')
  return baz(&g0, &g1, &g2);
}

// DexExpectWatchValue('accuml', '0', '1', '2', from_line=13, to_line=30)
// DexExpectWatchValue('extra', '0', '3', '7', from_line=13, to_line=30)
// DexExpectWatchValue('inbranch', '0', '20', from_line=13, to_line=30)
// DexExpectWatchValue('g0', '0', from_line=1, to_line=50)
// DexExpectWatchValue('g1', '0', '1', from_line=1, to_line=50)
// DexExpectWatchValue('g2', '0', '2', from_line=1, to_line=50)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
