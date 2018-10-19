int add(const int x, const int y) {
  int z = x + y; // DexWatch('x', 'y', 'z')
  return z;      // DexWatch('x', 'y') # DexWatch('z')
}

int main(int argc, const char * argv[]) {
  return add(argc, argc+5);
}

// DexExpectWatchValue('x', '0',      from_line=2, to_line=3)
// DexExpectWatchValue('y', '5',      from_line=2, to_line=3)
// DexExpectWatchValue('z', '0', '5', from_line=2, to_line=3)
