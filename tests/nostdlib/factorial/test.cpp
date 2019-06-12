// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
unsigned long Factorial(int n) {
	volatile unsigned long fac = 1; // DexWatch('n')

	for (int i = 1; i <= n; ++i)
		fac *= i; // DexWatch('i', 'n', 'fac')

	return fac; // DexWatch('n', 'fac')
}

int main()
{
	return Factorial(8);
}


// DexExpectWatchValue('n', '8', on_line=9)

// DexExpectWatchValue('i', '1', '2', '3', '4', '5', '6', '7', '8', on_line=12)
// DexExpectWatchValue('fac', '1', '2', '6', '24', '120', '720', '5040', on_line=12)
// DexExpectWatchValue('n', '8', on_line=12)

// DexExpectWatchValue('fac', '40320', on_line=14)
// DexExpectWatchValue('n', '8', on_line=14)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
