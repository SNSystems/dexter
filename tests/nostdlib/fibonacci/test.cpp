#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
void Fibonacci(int terms, int& total)
{
	int first = 0;
	int second = 1;

	for (int i = 0; i < terms; ++i)
	{
		int next = first + second; // DexWatch('i', 'first', 'second', 'total')
		total += first;            // DexWatch('i', 'first', 'second', 'total', 'next')
		first = second;            // DexWatch('i', 'first', 'second', 'total', 'next')
		second = next;             // DexWatch('i', 'first', 'second', 'total', 'next')
	}
}

int main()
{
	int total = 0;
	Fibonacci(5, total);
	return total;  								// DexWatch('total')
}

// DexExpectWatchValue('i',      '0', '1', '2', '3', '4', from_line=15, to_line=18)
// DexExpectWatchValue('first',  '0', '1', '2', '3', '5', from_line=15, to_line=18)
// DexExpectWatchValue('second', '1', '2', '3', '5',      from_line=15, to_line=18)
// DexExpectWatchValue('total',  '0', '1', '2', '4', '7', from_line=15, to_line=18)
// DexExpectWatchValue('next',   '1', '2', '3', '5', '8', from_line=16, to_line=18)
// DexExpectWatchValue('total',  '7', on_line=26)
// DexExpectStepKind('FUNC_EXTERNAL', 0)
