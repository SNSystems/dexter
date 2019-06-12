// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

#include <vector>

struct Foo
{
	DEX_NOINLINE
	int Do(const int& val)
	{
		return val * 2;
	}

	int Bar(const std::vector<Foo*>& vecFoos)
	{
		int val = 1;

		for (auto pFoo : vecFoos)
			val += pFoo->Do(val); // DexWatch('pFoo != 0', 'val')

		return val; // DexWatch('val', '&vecFoos != 0')
	}
};

int main()
{
	std::vector<Foo*> vecFoos;

	for (int i = 0; i < 2; i++)
		vecFoos.push_back(new Foo);

	int val = 0;

	for (auto pFoo : vecFoos)
		val += pFoo->Bar(vecFoos); // DexWatch('pFoo != 0', 'val')

	return val; // DexWatch('val')
}


// DexExpectWatchValue('val', '1', '3', '1', '3', on_line=22)
// DexExpectWatchValue('pFoo != 0', 'true', on_line=22)

// DexExpectWatchValue('val', '9', on_line=24)
// DexExpectWatchValue('&vecFoos != 0', 'true', on_line=24)

// DexExpectWatchValue('pFoo != 0', 'true', on_line=38)
// DexExpectWatchValue('val', '0', '9', on_line=38)
// DexExpectWatchValue('val', '18', on_line=40)
