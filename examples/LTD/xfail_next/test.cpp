
int main()
{
    int a = 0;
    a = 1;          // DexWatch('a')
    a = 2;          // DexWatch('a')
    return 0;       // DexWatch('a')
}

// DexVerify(Eventually(And(Expect('a', '0'), Next(Eventually(Expect('a', '0'))))))
