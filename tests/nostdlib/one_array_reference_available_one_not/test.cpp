#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

struct Foo
{
	DEX_NOINLINE
	int Do(const int& val)
	{
		return val * 10; // DexWatch('val')
	}
};

int main()
{
	int idx = 0;

	int array1[2] = { 5, 10 };
	Foo* array2[2] = { new Foo(), new Foo() };

	int& valA = array1[1 - idx];
	int& valB = array1[idx];

	Foo* pFoo1 = array2[1 - idx];
	Foo* pFoo2 = array2[idx];

	return valA + valB + pFoo1->Do(valA) + pFoo2->Do(valB); // DexWatch('valA', 'valB', 'pFoo1 != 0', 'pFoo2 != 0')
}


// DexExpectWatchValue('val', '10', '5', on_line=12)

// DexExpectWatchValue('pFoo1 != 0', 'true', on_line=29)
// DexExpectWatchValue('pFoo2 != 0', 'true', on_line=29)
// DexExpectWatchValue('valA', '10', on_line=29)
// DexExpectWatchValue('valB', '5', on_line=29)