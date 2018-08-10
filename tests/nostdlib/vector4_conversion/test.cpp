#include "header.h"

int main() {
  float MyVar = get()[0];
  if (MyVar)  // DexWatch('MyVar')
    return 1;
}

// DexExpectWatchValue('MyVar', '1.10000002')
