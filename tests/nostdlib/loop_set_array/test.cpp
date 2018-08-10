int main()
{
    int aiSizes[127];

    for (int i = 0; i < 127; ++i)
    {
        aiSizes[i] = i; // DexWatch('i')
    }
    return aiSizes[12];  // DexWatch('aiSizes[0]', 'aiSizes[126]')
}

// DexExpectWatchValue('aiSizes[0]',   0,   on_line=9)
// DexExpectWatchValue('aiSizes[126]', 126, on_line=9)
