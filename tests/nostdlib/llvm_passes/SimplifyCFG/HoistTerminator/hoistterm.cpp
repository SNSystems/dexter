// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  volatile int bar = 8;

  int read = foo;
  int read1 = bar;       // DexWatch('read')
  int read2 = bar;       // DexWatch('read', 'read1')
  int read3 = bar;       // DexWatch('read', 'read1')
  int read4 = bar;       // DexWatch('read', 'read1')
  int output = 0;        // DexWatch('read', 'read1')

  switch (read) {        // DexWatch('read', 'read1', 'output')
  case 0:
    output = read1 + 1;
    output >>= 1;
    break;
  case 1:
    output = read2 + 2;
    output >>= 1;
    break;
  case 2:
    output = read3 + 3;
    output >>= 1;
    break;
  case 3:
    output = read4 + 4;
    output >>= 1;
    break;
  case 4:               // DexWatch('read', 'read1', 'output')
    output = read1 + 5; // DexWatch('read', 'read1', 'output')
    output >>= 1;       // DexWatch('read', 'read1', 'output')
    break;              // DexWatch('read', 'read1', 'output')
  case 5:
    output = read2 + 6;
    output >>= 1;
    break;
  case 6:
    output = read3 + 7;
    output >>= 1;
    break;
  case 7:
  default:
    output = read4 + 8;
    output >>= 1;
    break;
  }
  output *= 2;     // DexWatch('read', 'read1', 'output')
  return output;   // DexWatch('read', 'read1', 'output')
}

// This tests that the multiply and return get hoisted into switch branches.
// Excitingly, the shift and multiply get merged, and some Advanced (TM)
// dwarf is used to represent different insns.

// DexExpectWatchValue('output', '0', '13', '6', '12')
// DexExpectWatchValue('read', '4')
// DexExpectWatchValue('read1', '8')
// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
