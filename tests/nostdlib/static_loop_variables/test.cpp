int Foo(int, int);

int main()
{
  return Foo(5, 6);
}

// DexExpectStepKind('FUNC_EXTERNAL', 0)
