
int main()
{
    int a = 0;
    a = 1;          // DexWatch('a')
    a = 2;          // DexWatch('a')
    return 0;       // DexWatch('a')
}

// DexVerify(After(Expect('a', '0'), Expect('a', '0')))
