// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

struct Foo
{
	int a, b;
};

DEX_NOINLINE
int Bar(const Foo& fooA, const Foo& fooB)
{
	return fooA.a + fooA.b * fooB.a + fooB.b; // DexWatch('fooA.a', 'fooA.b', 'fooB.a', 'fooB.b')
}

int main()
{
	int val = 0;

	for (int i = 0; i < 3; i++)
	{
		const Foo& fooA = { 10, 10 };
		const Foo& fooB = { 20, 20 };
		val += Bar(fooA, fooB); // DexWatch('val', 'fooA.a', 'fooA.b', 'fooB.a', 'fooB.b')
	}

	return val; // DexWatch('val')
}


// DexExpectWatchValue('fooA.a', '10', on_line=15)
// DexExpectWatchValue('fooA.b', '10', on_line=15)
// DexExpectWatchValue('fooB.a', '20', on_line=15)
// DexExpectWatchValue('fooB.b', '20', on_line=15)

// DexExpectWatchValue('val', '0', '230', '460', on_line=26)

// DexExpectWatchValue('fooA.a', '10', on_line=26)
// DexExpectWatchValue('fooA.b', '10', on_line=26)
// DexExpectWatchValue('fooB.a', '20', on_line=26)
// DexExpectWatchValue('fooB.b', '20', on_line=26)

// DexExpectWatchValue('val', '690', on_line=29)


// DexExpectStepKind('FUNC_EXTERNAL', 0)
// DexExpectStepKind('SAME', 0)
