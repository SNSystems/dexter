#include "header.h"

DEX_NOINLINE
void Fibonacci(int terms, int& total)
{
	int first = 0;
	int second = 1;

	for (int i = 1; i <= terms; ++i)
	{
		int next = first + second; // DexWatch('i', 'first', 'second', 'total')
		total += first;            // DexWatch('i', 'first', 'second', 'next', 'total')
		first = second;            // DexWatch('i', 'first', 'second', 'next', 'total')
		second = next;             // DexWatch('i', 'first', 'second', 'next', 'total')
	}
}


// DexExpectWatchValue('first', '0', '1', '2', '3', '5', from_line=11, to_line=14)
// DexExpectWatchValue('second', '1', '2', '3', '5', from_line=11, to_line=14)
// DexExpectWatchValue('total', '0', '1', '2', '4', '7', from_line=11, to_line=14)
// DexExpectWatchValue('i', '1', '2', '3', '4', '5', from_line=11, to_line=14)
// DexExpectWatchValue('next', '1', '2', '3', '5', '8', from_line=12, to_line=14)