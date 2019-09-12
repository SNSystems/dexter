// Check a returned struct small enough to fit into a single register can still
// be debugged effectively.

struct foo {
  ~foo() = default;

  foo()
    : a(0), b(0) {}

  foo(const int n_a, const int n_b)
    : a(n_a), b(n_b) {}

  foo(const foo & RHS) = default;

  foo & operator=(const foo & RHS) = default;

  int a, b;
};

foo GetFoo(const int arg) {
  foo aFooForYou(arg, arg + 1);
  return aFooForYou;
}

int main(const int argc, const char * argv[]) {
  foo localFoo;
  localFoo = GetFoo(argc);    // DexLabel('start')
  return localFoo.a + localFoo.b; // DexLabel('end')
}

// DexExpectWatchType('localFoo', 'foo', from_line='start', to_line='end')
// DexExpectWatchType('localFoo.a', 'int', from_line='start', to_line='end')
// DexExpectWatchType('localFoo.b', 'int', from_line='start', to_line='end')
// DexExpectWatchValue('localFoo.a', 0, 1, from_line='start', to_line='end')
// DexExpectWatchValue('localFoo.b', 0, 2, from_line='start', to_line='end')
