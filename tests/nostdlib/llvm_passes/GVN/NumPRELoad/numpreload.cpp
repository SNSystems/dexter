// RUN: %dexter
int foo = 0;
int randomglobal = 0;
bool bar = true;
int
baz(int *ptr)
{
  int qux = 0, quux = 0, corge;
  volatile int zero = 0;
  volatile int four = 4;
  volatile int five = 5;

  corge = zero;      // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  if (bar) {         // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux = *ptr;      // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux = four;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux += corge;    // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  } else {           // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux = five;      // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux = five;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux += corge;   // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  }                  // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  qux += five;       // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  corge = *ptr;      // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')

  foo += qux + quux + corge; // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  return foo; // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
}

int
baz2(int *ptr)
{
  int qux = 0, quux = 0, corge;
  volatile int zero = 0;
  volatile int four = 4;
  volatile int five = 5;

  corge = zero;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  if (bar) {        // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux = *ptr;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux = four;    // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux += corge;   // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  } else {          // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    qux = five;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux = five;    // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
    quux += corge;  // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  }                 // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  qux += five;      // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  corge = *ptr;     // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')

  foo += qux + quux + corge; // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
  return foo; // DexWatch('ptr', '*ptr', 'foo', 'corge', 'qux', 'quux')
}

int
main(int argc, char **argv)
{
  volatile int bees = 8;
  randomglobal = bees;
  int xyzzy = baz(&randomglobal);
  foo = 0;
  bar = false;
  randomglobal = bees;
  xyzzy += baz2(&randomglobal);
  return xyzzy;
}

// NB: clang head (2018-07-30 ish) labels the hoisted load of *ptr as being
// the value for corge, before it's assigned to. (In baz 1)

// First 'baz' call:
// BADExpectWatchValue('ptr', '&randomglobal', from_line=13, to_line=28)
// DexExpectWatchValue('*ptr', '8', from_line=13, to_line=28)
// DexExpectWatchValue('foo', '0', '25', from_line=13, to_line=28)
// DexExpectWatchValue('corge', '0', from_line=13, to_line=24)
// DexExpectWatchValue('corge', '8', from_line=25, to_line=28)
// DexExpectWatchValue('qux', '0', '8', '13', from_line=13, to_line=28)
// DexExpectWatchValue('quux', '0', '4', from_line=13, to_line=28)

// BADExpectWatchValue('ptr', '&randomglobal', from_line=38, to_line=52)
// DexExpectWatchValue('*ptr', '8', from_line=38, to_line=52)
// DexExpectWatchValue('foo', '0', '23', from_line=38, to_line=52)
// DexExpectWatchValue('corge', '0', from_line=38, to_line=49)
// DexExpectWatchValue('corge', '8', from_line=50, to_line=52)
// DexExpectWatchValue('qux', '0', '5', '10', from_line=38, to_line=52)
// DexExpectWatchValue('quux', '0', '5', from_line=38, to_line=52)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('BACKWARD', 0)
