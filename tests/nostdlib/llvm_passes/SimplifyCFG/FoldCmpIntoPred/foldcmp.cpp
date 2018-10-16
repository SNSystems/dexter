// RUN: %dexter
int xyzzy(int &other, int *foo)
{
  volatile int blah = 8;  // DexWatch('other', '*foo')

  int read = *foo;        // DexWatch('other', '*foo', 'blah')
  int tmp = other;        // DexWatch('other', '*foo', 'blah', 'read')

  if (read == 4) {        // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    *foo = 5;             // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    tmp += 3;             // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  }                       // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  switch (read) {         // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 1:                 // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += 2;           // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 2:                 // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += 3;           // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 3:                 // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += 4;           // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 4:                 // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    tmp /= 3;             // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += blah;        // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    tmp -= 1;             // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 5:                 // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += 12;          // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  case 12:                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other += 5;           // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  default:                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    other = 0;            // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
    break;                // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  }

  *foo += tmp;            // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
  return *foo;            // DexWatch('other', '*foo', 'blah', 'read', 'tmp')
}

int
main()
{
  int lolwat = 4, trains = 4;
  xyzzy(lolwat, &trains);   // DexWatch('lolwat', 'trains')
  return lolwat;            // DexWatch('lolwat', 'trains')
}

// DexExpectWatchValue('other', '4', '12', from_line=2, to_line=41)
// DexExpectWatchValue('*foo', '4', '5', '6', from_line=2, to_line=41)
// DexExpectWatchValue('read', '4', from_line=6, to_line=17)
// DexExpectWatchValue('tmp', '4', '7', '2', '1', from_line=2, to_line=41)
// DexExpectWatchValue('blah', '8', from_line=2, to_line=41)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 3)
