// Test debugging experience of structs when passed by RVO.

int global = 0;

struct Foo {
  Foo() {
    for ( size_t ix = 0; ix != aSize; ++ix)
      a[ix] = ix;
  }

  ~Foo() = default;

  Foo(const Foo & RHS) {
    // if global is not 0 then RVO did not happen.
    global = 1;
  }
  Foo(Foo && RHS) {
    // if global is not 0 then RVO did not happen.
    global = 2;
  }

  Foo & operator=(const Foo & RHS) = default;

  static const size_t aSize = 33;
  int a[aSize];
};

// return a foo by value.
Foo GetFoo(const int arg) {
  Foo aFooForYou;
  aFooForYou.a[8] += arg;
  return aFooForYou;
}

int main(const int argc, const char * argv[]) {
  Foo pleaseRVOMe = GetFoo(argc);
  return pleaseRVOMe.a[5] +   // DexLabel('start')
         pleaseRVOMe.a[8];    // DexLabel('end')
}

// DexExpectWatchType('pleaseRVOMe', 'Foo', from_line='start', to_line='end')
// DexExpectWatchValue('pleaseRVOMe.a[5]', 5, from_line='start', to_line='end')
// DexExpectWatchValue('pleaseRVOMe.a[8]', 9, from_line='start', to_line='end')
// DexExpectWatchValue('global', 0, from_line='start', to_line='end')
