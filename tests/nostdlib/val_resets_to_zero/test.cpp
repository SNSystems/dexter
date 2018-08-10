#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
int FuncA(const int& a)
{
	return a * 10; // DexWatch('a')
}

int main(int argc, char** argv)
{
	int val = 0;

	for (int i = 0; i < argc + 2; ++i)
		val += FuncA(i); // DexWatch('i', 'val')

	return val; // DexWatch('val')
}


// DexExpectWatchValue('a', '0', '1', '2', on_line=10)

// DexExpectWatchValue('val', '0', '10', on_line=18)
// DexExpectWatchValue('i', '0', '1', '2', on_line=18)

// DexExpectWatchValue('val', '30', on_line=20)


// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('SAME', 0)