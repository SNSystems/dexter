// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

#include <vector>
#include <memory>

struct Foo
{
	DEX_NOINLINE
	int Do(const int& val)
	{
		return val * 2; // DexWatch('val')
	}

	DEX_NOINLINE
	int Bar(const std::vector<std::shared_ptr<Foo>>& vecFoos)
	{
		int val = 0;

		for (auto spFoo : vecFoos)
			val += spFoo->Do(val); // DexWatch('&vecFoos != 0', '&spFoo != 0', 'val')

		return val; // DexWatch('val')
	}
};

int main()
{
	std::vector<std::shared_ptr<Foo>> vecFoos;

	for (int i = 0; i < 2; i++)
		vecFoos.push_back(std::make_shared<Foo>()); // DexWatch('&vecFoos != 0', 'i')

	int val = 0;

	for (auto spFoo : vecFoos)
		val += spFoo->Bar(vecFoos); // DexWatch('&vecFoos != 0', '&spFoo != 0', 'val')

	return val; // DexWatch('val')
}


// DexExpectWatchValue('val', '0', on_line=15)

// DexExpectWatchValue('&vecFoos != 0', 'true', on_line=24)
// DexExpectWatchValue('&spFoo != 0', 'true', on_line=24)
// DexExpectWatchValue('val', '0', on_line=24)

// DexExpectWatchValue('val', '0', on_line=26)

// DexExpectWatchValue('i', '0', '1', on_line=35)
// DexExpectWatchValue('&vecFoos != 0', 'true', on_line=35)

// DexExpectWatchValue('&vecFoos != 0', 'true', on_line=40)
// DexExpectWatchValue('&spFoo != 0', 'true', on_line=40)
// DexExpectWatchValue('val', '0', on_line=40)

// DexExpectWatchValue('val', '0', on_line=42)
