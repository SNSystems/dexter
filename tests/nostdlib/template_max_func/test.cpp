#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

template <typename T>
DEX_NOINLINE
T const& Max(T const& a, T const& b)
{
	return a < b ? b : a; // DexWatch('a', 'b')
}

int main(int argc, char** argv)
{
	int i0 = 39;
	int i1 = 20;

	int i2 = 11;
	int i3 = 56;

	return Max(i0, i1) + Max(i2, i3); // DexWatch('i0', 'i1', 'i2', 'i3')
}


// DexExpectWatchValue('a', '39', '11', on_line=11)
// DexExpectWatchValue('b', '20', '56', on_line=11)

// DexExpectWatchValue('i0', '39', on_line=22)
// DexExpectWatchValue('i1', '20', on_line=22)
// DexExpectWatchValue('i2', '11', on_line=22)
// DexExpectWatchValue('i3', '56', on_line=22)