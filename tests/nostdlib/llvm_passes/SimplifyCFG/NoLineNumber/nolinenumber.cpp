// RUN: %dexter
// This program, when compiled
// /fast/fs/debug/bin/clang++ test3.cpp -g -O2 -o a.out -fno-inline
// with clang/llvm of about 2018-09-01, does not have a line number on the
// first instruction of main. Not clear whether this is really a bug
// or not... but at the very least, running 'start' in gdb does _not_ give you
// a line number, which threw me.
//
// Dexter doesn't seem to pick this up.

int
main(int argc, char **argv)
{

  int beards = 0;
  if (argc == 4) // DexExpectStepOrder(1)
    beards = 8 + **argv;
  else
    beards = 4 - **argv;

  return beards; // DexExpectStepOrder(2)
}

