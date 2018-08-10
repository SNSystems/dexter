#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

class Bar
{
public:
	DEX_NOINLINE
	void Do()
	{
	}
};

class Foo
{
public:
	DEX_NOINLINE
	Foo()
	{
		m_pBar1 = new Bar;
		m_pBar2 = new Bar; // DexWatch('m_pBar1 != 0')
	}

	int FuncA(const int& a)
	{
		m_pBar1->Do();
		m_pBar2->Do();
		return a * 10; // DexWatch('a', 'm_pBar1 != 0', 'm_pBar2 != 0')
	}

private:
	union
	{
		Bar* m_pBar2;
	};

	Bar* m_pBar1;
};

int main(int argc, char** argv)
{
	Foo* foo = new Foo;
	return foo->FuncA(argc); // DexWatch('foo != 0')
}


// DexExpectWatchValue('m_pBar1 != 0', 'true', on_line=23)

// DexExpectWatchValue('a', '1', on_line=30)
// DexExpectWatchValue('m_pBar1 != 0', 'true', on_line=30)
// DexExpectWatchValue('m_pBar2 != 0', 'true', on_line=30)

// DexExpectWatchValue('foo != 0', 'true', on_line=45)


// DexExpectStepKind('SAME', 0)
// DexExpectStepKind('BACKWARD', 0)