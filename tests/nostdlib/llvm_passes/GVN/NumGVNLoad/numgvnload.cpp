// RUN: %dexter
int foo = 0;
int randomglobal = 0;
bool bar = true;
int
baz(int *ptr)
{
  int qux = 0, quux = 0, corge = 0;
  volatile int zero = 0;
  volatile int four = 4;
  volatile int five = 5;

  // Load of ptr below gets eliminated by gvn.
  // Not clear what debug information could go wrong here.
  if (bar) {          // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
    qux = *ptr;       // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
    quux = four;      // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
  } else {            // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
    qux = five;       // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
    quux = *ptr;      // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
  }                   // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
  qux += quux;        // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
  corge = *ptr;       // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')

  foo += qux + corge; // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
  return foo;         // DexWatch('ptr', '*ptr', 'qux', 'quux', 'corge', 'foo')
}

int
main(int argc, char **argv)
{
  volatile int bees = 8;
  randomglobal = bees;
  int xyzzy = baz(&randomglobal);
  return xyzzy;
}

// First 'baz' call:
// DexExpectWatchValue('*ptr', '8', from_line=15, to_line=27)
// DexExpectWatchValue('foo', '0', '20', from_line=15, to_line=27)
// DexExpectWatchValue('corge', '0', from_line=15, to_line=23)
// DexExpectWatchValue('corge', '8', from_line=24, to_line=27)
// DexExpectWatchValue('qux', '0', '8', '12', from_line=15, to_line=27)
// DexExpectWatchValue('quux', '0', '4', from_line=15, to_line=27)
