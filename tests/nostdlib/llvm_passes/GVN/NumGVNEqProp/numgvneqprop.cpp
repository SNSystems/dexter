// RUN: %dexter
#include <stdio.h>
volatile int foo = 4;

int func1(int load1, int accuml1) // DexWatch('load1', 'accuml1')
{                                 // DexWatch('load1', 'accuml1')
  if (load1 == 4) {               // DexWatch('load1', 'accuml1')
    accuml1 += load1 + load1;     // DexWatch('load1', 'accuml1')
    accuml1 %= load1;             // DexWatch('load1', 'accuml1')
  }                               // DexWatch('load1', 'accuml1')
  return accuml1;                 // DexWatch('load1', 'accuml1')
}

int func2(int load2, int accuml2)         // DexWatch('bin', 'load2', 'accuml2')
{                                         // DexWatch('bin', 'load2', 'accuml2')
  // Bin here breaks some optimisations deliberately
  static volatile int bin = 0;            // DexWatch('bin', 'load2', 'accuml2')
  if (load2 == 4) {                       // DexWatch('bin', 'load2', 'accuml2')
    accuml2 += (load2 < 10) ? load2 : 0;  // DexWatch('bin', 'load2', 'accuml2')
    printf("also clobber\n");             // DexWatch('bin', 'load2', 'accuml2')
    bin = accuml2;                        // DexWatch('bin', 'load2', 'accuml2')
    accuml2 += (load2 > 1) ? accuml2 : 0; // DexWatch('bin', 'load2', 'accuml2')
  }                                       // DexWatch('bin', 'load2', 'accuml2')
  return accuml2;                         // DexWatch('bin', 'load2', 'accuml2')
}

int func4(int load4, int load5, int acc3, int acc4) // DexWatch('load4', 'load5', 'acc3', 'acc4')
{                                  // DexWatch('load4', 'load5', 'acc3', 'acc4')
  if (load4 == load5) {            // DexWatch('load4', 'load5', 'acc3', 'acc4')
    printf("clobber all\n");       // DexWatch('load4', 'load5', 'acc3', 'acc4')
    acc3 += load4;                 // DexWatch('load4', 'load5', 'acc3', 'acc4')
    acc4 += load5;                 // DexWatch('load4', 'load5', 'acc3', 'acc4')
    acc3 += load4 + load5;         // DexWatch('load4', 'load5', 'acc3', 'acc4')
  }                                // DexWatch('load4', 'load5', 'acc3', 'acc4')

  return (acc3 | acc4) + load4;    // DexWatch('load4', 'load5', 'acc3', 'acc4')
}

int
main()
{
  int bar = foo, baz = foo; // DexWatch('foo', 'bar', 'baz')

  bar = func1(foo, bar);             // DexWatch('foo', 'bar', 'baz')
  baz = func2(foo, baz);             // DexWatch('foo', 'bar', 'baz')
  int tmp = foo;                     // DexWatch('foo', 'bar', 'baz') 
  baz = func4(tmp, foo, bar, baz);   // DexWatch('foo', 'bar', 'baz', 'tmp')

  return baz;                        // DexWatch('foo', 'bar', 'baz', 'tmp')
}

// DexExpectWatchValue('load1', '4', from_line=5, to_line=12)
// DexExpectWatchValue('accuml1', '4', '12', '0', from_line=5, to_line=12)
// DexExpectWatchValue('load2', '4', from_line=14, to_line=25)
// DexExpectWatchValue('accuml2', '4', '8', '16', from_line=14, to_line=25)
// DexExpectWatchValue('bin', '0', '8', from_line=14, to_line=25)
// DexExpectWatchValue('load4', '4', from_line=27, to_line=37)
// DexExpectWatchValue('load5', '4', from_line=27, to_line=37)
// DexExpectWatchValue('acc3', '0', '4', '12', from_line=27, to_line=37)
// DexExpectWatchValue('acc4', '16', '20', from_line=27, to_line=37)

// DexExpectWatchValue('bar', '4', '0', from_line=40, to_line=50)
// DexExpectWatchValue('baz', '4', '16', '32', from_line=40, to_line=50)
