// RUN: %dexter

#include "header.h"

int main()
{
	int total = 0;
	Fibonacci(5, total);
	return total; // DexWatch('total')
}


// DexExpectWatchValue('total', '7', on_line=7)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
