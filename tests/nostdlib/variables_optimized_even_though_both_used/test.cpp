// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

#include <math.h>

struct Foo
{
	double a, b;

	DEX_NOINLINE
	int FooBar(const Foo& foo) const
	{
		double da = a - foo.a;
		double db = b - foo.b;
		return sqrt(da * da + db * db); // DexWatch('foo', 'a', 'b', 'da', 'db')
	}
};

int main()
{
	Foo foo1 = { 12.3, 24.9 };
	Foo foo2 = { 90.7, 3.1 };
	return foo1.FooBar(foo2); // DexWatch('foo1', 'foo2')
}


// DexExpectWatchValue('db', '21.799999999999997', on_line=18)
// DexExpectWatchValue('a', '12.300000000000001', on_line=18)
// DexExpectWatchValue('da', '-78.400000000000006', on_line=18)
// DexExpectWatchValue('b', '24.899999999999999', on_line=18)

// DexExpectStepKind('BACKWARD', 0)
