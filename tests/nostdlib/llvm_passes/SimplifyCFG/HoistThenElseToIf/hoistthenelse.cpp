// RUN: %dexter
int
main()
{
  volatile int foo = 4;
  volatile int blah = 10; // DexWatch('foo')
  volatile int xyzzy = 12;// DexWatch('foo')
  volatile int lame = 100;// DexWatch('foo')

  int read1 = blah;       // DexWatch('foo')
  int read2 = xyzzy;      // DexWatch('foo', 'read1')
  int read3 = lame;       // DexWatch('foo', 'read1', 'read2')

  int calc1 = 0;          // DexWatch('foo', 'read1', 'read2', 'read3')

  if (foo == 10) {        // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 = read1;        // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 += read2;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 += read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')

    calc1 *= read1;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 /= read2;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')

    calc1 -= read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 *= read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
  } else {
    calc1 = read1;        // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 += read2;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 += read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')

    calc1 *= read1;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 /= read2;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')

    calc1 += read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
    calc1 /= read3;       // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
  }

  return calc1;           // DexWatch('foo', 'read1', 'read2', 'read3', 'calc1')
}
// This test contains a ton of duplicate code between two paths down a branch,
// which all gets hoisted. The debug _value_ information gets kept around, which
// is correct, but all the line numbers go, which means the values can't be
// observed.

// DexExpectWatchValue('calc1', '0', '10', '22', '122', '1220', '101', '201', '2', from_line=1, to_line=50)
// DexExpectWatchValue('read1', '10', from_line=1, to_line=50)
// DexExpectWatchValue('read2', '12', from_line=1, to_line=50)
// DexExpectWatchValue('read3', '100', from_line=1, to_line=50)
// DexExpectWatchValue('foo', '4', from_line=1, to_line=50)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('VERTICAL_BACKWARD', 0)
