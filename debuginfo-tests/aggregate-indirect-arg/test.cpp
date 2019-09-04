// REQUIRES: linux, clang, lldb
//
// RUN: dexter.py test --fail-lt 1.0 -w \
// RUN:     --builder clang --debugger lldb --cflags "-O0 -g" -- %S
// Radar 8945514
// DEBUGGER: break 22
// DEBUGGER: r
// DEBUGGER: p v
// CHECK: ${{[0-9]+}} =
// CHECK:  Data ={{.*}} 0x0{{(0*)}}
// CHECK:  Kind = 2142

class SVal {
public:
  ~SVal() {}
  const void* Data;
  unsigned Kind;
};

void bar(SVal &v) {}
class A {
public:
  void foo(SVal v) { bar(v); } // DexLabel('foo')
};

int main() {
  SVal v;
  v.Data = 0;
  v.Kind = 2142;
  A a;
  a.foo(v);
  return 0;
}

/*
DexExpectProgramState({
  'frames': [
    {
      'location': { 'lineno': 'foo' },
      'watches': {
        'v.Data == 0': 'true',
        'v.Kind': '2142'
      }
    }
  ]
})
*/

