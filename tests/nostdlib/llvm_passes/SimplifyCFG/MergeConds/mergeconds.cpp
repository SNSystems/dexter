// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  int read = foo;
  int more = foo;    // DexWatch('read')

  more += 4;         // DexWatch('read', 'more')
  if (read == 4) {   // DexWatch('read', 'more')
    more -= 3;       // DexWatch('read', 'more')
  }                  // DexWatch('read', 'more')

  more %= 12;        // DexWatch('read', 'more')
  if (read == 4) {   // DexWatch('read', 'more')
    more *= 12;      // DexWatch('read', 'more')
  }                  // DexWatch('read', 'more')

  return more;       // DexWatch('read', 'more')
}

// Most of what goes wrong here is to do with stepping backwards.

// DexExpectWatchValue('read', '4', from_line=1, to_line=50)
// DexExpectWatchValue('more', '4', '8', '5', '60', from_line=1, to_line=50)
// DexExpectStepKind('BACKWARD', 0)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
