#include <deque>

struct A {
  int a;
  A(): a(0) {}
  A(int a) : a(a) {}
};

using deq_t = std::deque<A>;

template class std::deque<A>;

static void __attribute__((noinline, optnone)) escape(deq_t &deq) {
  static volatile deq_t *sink;
  sink = &deq;
}

int main() {
  deq_t deq;
  deq.push_back(1234);
  deq.push_back(56789);
  escape(deq);
  while (!deq.empty()) {
    auto record = deq.front();
    deq.pop_front();
    escape(deq);
  }
}

// DexExpectWatchValue('deq[0].a', '1234', on_line=22)
// DexExpectWatchValue('deq[1].a', '56789', on_line=22)

// DexExpectWatchValue('deq[0].a', '56789', '0', on_line=26)

