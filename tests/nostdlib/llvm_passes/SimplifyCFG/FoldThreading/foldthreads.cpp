// RUN: %dexter
int
main()
{
  volatile int foo = 4;

  int read = foo;
  int read1 = foo;        // DexWatch('read')
  int read2 = foo;        // DexWatch('read', 'read1')
  int something = 0;      // DexWatch('read', 'read1', 'read2')
  int beards = 0, another = 0; // DexWatch('read', 'read1', 'read2', 'something')

  if (read == 4) {        // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    something = 4;        // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    beards = read1 * 2;   // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    another = read2 * 2;  // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
  } else {                // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    something = read;     // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    beards = read1 / 2;   // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    another = read2 / 2;  // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
  }                       // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')

  beards &= 0xffff;       // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')

  if (something == 4) {   // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    beards += something + another; // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
  } else {                // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
    beards -= something + another; // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
  }                       // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')

  return beards;          // DexWatch('read', 'read1', 'read2', 'something', 'beards', 'another')
}

// With clang++-6.0 this reports that 'another' always has the value zero.
// With almost-7.0 it reports that 'another' is always '2'!
//
// Reported: https://bugs.llvm.org/show_bug.cgi?id=38754

// DexExpectWatchValue('read', '4', from_line=1, to_line=50)
// DexExpectWatchValue('read1', '4', from_line=1, to_line=50)
// DexExpectWatchValue('read2', '4', from_line=1, to_line=50)
// DexExpectWatchValue('something', '0', '4', from_line=1, to_line=50)
// DexExpectWatchValue('beards', '0', '8', '20', from_line=1, to_line=50)
// DexExpectWatchValue('another', '0', '8', from_line=1, to_line=50)
// DexExpectStepKind('FUNC', 1)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
