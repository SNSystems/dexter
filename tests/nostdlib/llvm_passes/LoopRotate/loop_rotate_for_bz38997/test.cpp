// RUN: %dexter

int simple(int arg) {
  return arg;
}

int start = 0;

int foo_for(int count) {
  int result = 0;                                         // DexWatch('start', 'count', 'result')
  for (unsigned long long ix = start; ix != count; ++ix)  // DexWatch('start', 'count', 'result', 'ix')
    result += simple(ix);                                 // DexWatch('start', 'count', 'result', 'ix')
  return result;                                          // DexWatch('start', 'count', 'result')
}

int main(int argc, const char ** argv) {
  int loopBy = argc + 3;
  return foo_for(loopBy);
}

// DexExpectWatchValue('start',  '0',                from_line=10, to_line=13)
// DexExpectWatchValue('count',  '4',                from_line=10, to_line=13)
// DexExpectWatchValue('result', '0', '1', '3', '6', from_line=10, to_line=13)
// DexExpectWatchValue('ix',     '0', '1', '2', '3', from_line=11, to_line=12)
