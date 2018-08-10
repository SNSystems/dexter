#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
int CalculatePower(int base, int power)
{
	if (power == 1)
		return 1; // DexWatch('base', 'power')

	return base * CalculatePower(base, power - 1); // DexWatch('base', 'power')
}

int main(int argc, char** argv)
{
	return CalculatePower(argc + 2, 10);
}


// DexExpectWatchValue('base', '3', on_line=11)
// DexExpectWatchValue('power', '1', on_line=11)

// DexExpectWatchValue('base', '3', on_line=13)
// DexExpectWatchValue('power', '10', '9', '8', '7', '6', '5', '4', '3', '2', '3', '4', '5', '6', '7', '8', '9', '10', on_line=13)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
