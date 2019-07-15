
int main()
{
    int a = 2;
    a = 2;          // DexWatch('a')
    a = 1;          // DexWatch('a')
    a = 1;          // DexWatch('a')
    return 0;       // DexWatch('a')
}

// DexVerify(Until(Expect('a', '0'), Expect('a', '1')))
