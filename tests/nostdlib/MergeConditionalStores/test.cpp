int global = 0;
struct thing_t
{
  int cap;
  int ret;
};
static thing_t fn_a(thing_t thing)
{
  if (thing.cap & 1) {
    thing.cap += 1;
    thing.ret += 1;
  } else {
    global = 2;
    thing.ret += 2;
  }
  return thing; // DexWatch("thing.cap", "thing.ret")
}
static thing_t fn_b(thing_t thing)
{
   if (thing.cap & 2) {
    thing.cap += 2;
    thing.ret += 3;
  } else {
    global = 5;
    thing.ret += 4;
  }
  return thing; // DexWatch("thing.cap", "thing.ret")
}

int main()
{
  volatile int generator = 4;
  int capture = generator;
  int retval = 0;
  thing_t thing = fn_a({capture, retval});
  thing = fn_b(thing);  // DexWatch("thing.cap", "thing.ret")
  return thing.ret;     // DexWatch("thing.cap", "thing.ret")
}

// Modifed version of Jeremy's bug report https://bugs.llvm.org/show_bug.cgi?id=38756

// DexExpectWatchValue("thing.cap", 4, on_line=16)
// DexExpectWatchValue("thing.ret", 2, on_line=16)
// DexExpectWatchValue("thing.cap", 4, on_line=36)
// DexExpectWatchValue("thing.ret", 2, on_line=36)

// DexExpectWatchValue("thing.cap", 4, on_line=27)
// DexExpectWatchValue("thing.ret", 6, on_line=27)
// DexExpectWatchValue("thing.cap", 4, on_line=37)
// DexExpectWatchValue("thing.ret", 6, on_line=37)

// Test run:
// python dexter.py test --builder clang --debugger lldb --cflags="-O0 -g" -v
// MergeConditionalStores: (1.0000)
//
// python dexter.py test --builder clang --debugger lldb --cflags="-O2 -g" -v
// MergeConditionalStores: (0.2857)
