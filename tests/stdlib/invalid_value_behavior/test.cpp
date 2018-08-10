#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

#include <vector>
#include <cstdio>

struct Foo
{
	int a, b;
};

struct Bar
{
	DEX_NOINLINE
	int Do(const Foo& fooA, const Foo& fooB)
	{
		return fooA.a + fooA.b * fooB.a + fooB.b; // DexWatch('fooA.a', 'fooA.b', 'fooB.a', 'fooB.b')
	}
};

DEX_NOINLINE
const Foo GetFoo()
{
	return { 10, 10 };
}

int main()
{
	Bar* pBar = new Bar;
	int val = 0;

	for (int i = 0; i < 10; i++)
	{
		const Foo& fooA = GetFoo();
		const Foo& fooB = GetFoo();
		val += pBar->Do(fooA, fooB); // DexWatch('i', 'val', 'fooA.a', 'fooA.b', 'fooB.a', 'fooB.b')
	}

	return val; // DexWatch('val')
}



// DexExpectWatchValue('fooA.a', '10', on_line=20)
// DexExpectWatchValue('fooA.b', '10', on_line=20)
// DexExpectWatchValue('fooB.a', '10', on_line=20)
// DexExpectWatchValue('fooB.b', '10', on_line=20)

// DexExpectWatchValue('val', '0', '120', '240', '360', '480', '600', '720', '840', '960', '1080', on_line=39)
// DexExpectWatchValue('i', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', on_line=39)

// DexExpectWatchValue('fooA.a', '10', on_line=39)
// DexExpectWatchValue('fooA.b', '10', on_line=39)
// DexExpectWatchValue('fooB.a', '10', on_line=39)
// DexExpectWatchValue('fooB.b', '10', on_line=39)

// DexExpectWatchValue('val', '1200', on_line=42)


// DexExpectStepKind('SAME', 0)