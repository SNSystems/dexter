__attribute__((noinline))
void do_something(short x) {
  volatile short g = x;
}

struct Basket {
  short apples;
  short bananas;
};

struct Box {
  Basket baskets[3];
};

__attribute__((noinline))
void foo(const Box& box)
{
  Basket basket = box.baskets[2];
  do_something(basket.apples); // DexLabel('a')

  basket.apples = 55;
  do_something(basket.apples); // DexLabel('b')

  basket.apples = basket.bananas;
  do_something(basket.apples); // DexLabel('c')
}

int main(){
  Box b {{
    { 1, 2 },
    { 10, 20 },
    { 100, 200 }
  }};

  foo(b);
  return 0;
}

// Compiling with `clang -g -O2 test.cpp`, basket.bananas is evaluated as '0' on
// lines 'b' and 'c'.
//
// basket.bananas results are broken with lldb:
// https://bugs.llvm.org/show_bug.cgi?id=43126
//
// basket.apples on line 'c' is broken because a dbg.value is dropped somewhere.


// DexExpectWatchValue('basket.apples', '100', on_line='a')
// DexExpectWatchValue('basket.bananas', '200', on_line='a')

// DexExpectWatchValue('basket.apples', '55', on_line='b')
// DexExpectWatchValue('basket.bananas', '200', on_line='b')

// DexExpectWatchValue('basket.apples', '200', on_line='c')
// DexExpectWatchValue('basket.bananas', '200', on_line='c')
