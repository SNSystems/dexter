
int main()
{
    int a = 0;
    a = 1;          // DexWatch('a')
    a = 2;          // DexWatch('a')
    a = 3;          // DexWatch('a')
    a = 4;          // DexWatch('a')
    a = 5;          // DexWatch('a')
    return 0;       // DexWatch('a')
}

// DexVerify(Eventually(Ordered(Expect('a', '3'), Expect('a', '1'), Expect('a', '5'))))
