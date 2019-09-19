// diamond cfg test for variable of struct type.

struct foo {
  int a;
  int b;
};


int main(const int argc, const char * argv[]) {

  foo a = {argc, argc + 1};
  foo b = {argc + 2, argc + 3};
  foo c;
  if (argc + 1 == 2) { // DexLabel('start')
    c = a;
  }
  else {
    c = b;
  }
  return c.a + c.b;    // DexLabel('end')
}

// DexExpectWatchType('a', 'foo', from_line='start', to_line='end')
// DexExpectWatchType('b', 'foo', from_line='start', to_line='end')
// DexExpectWatchType('c', 'foo', from_line='start', to_line='end')
// DexExpectWatchValue('c.a', 0, 1, from_line='start', to_line='end')
// DexExpectWatchValue('c.b', 0, 2, from_line='start', to_line='end')
