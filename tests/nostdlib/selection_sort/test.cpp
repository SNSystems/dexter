// RUN: %dexter

#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
void Swap(int* p1, int* p2)
{
	int tmp = *p1;
	*p1 = *p2;
	*p2 = tmp;
}

DEX_NOINLINE
void SelectionSort(int arr[], int n)
{
	for (int i = 0; i < n; i++)
	{
		int min = i; // DexWatch('i', 'n')

		for (int j = i + 1; j < n; j++)
		{
			if (arr[min] > arr[j]) // DexWatch('j', 'min', 'n', 'arr[min]', 'arr[j]')
				min = j;
		}

		Swap(&arr[min], &arr[i]); // DexWatch('min', 'n', 'arr[min]', 'arr[i]')
	}
}

int main()
{
	int arr1[5] = { 8, 1, 3, 9, 1 };
	SelectionSort(arr1, 5);
	return 0;  // DexWatch('arr1[0]', 'arr1[1]', 'arr1[2]', 'arr1[3]', 'arr1[4]')
}


// DexExpectWatchValue('n', '5', on_line=20)
// DexExpectWatchValue('i', '0', '1', '2', '3', '4', on_line=20)

// DexExpectWatchValue('j', '1', '2', '3', '4', '2', '3', '4', '3', '4', on_line=24)
// DexExpectWatchValue('min', '0', '1', '2', '3', '0', '1', '2', '3', on_line=24)
// DexExpectWatchValue('n', '5', on_line=24)
// DexExpectWatchValue('arr[min]', '8', '1', '8', '3', '9', on_line=24)
// DexExpectWatchValue('arr[j]', '1', '3', '9', '1', '3', '9', '1', '9', '8', '8', on_line=24)

// DexExpectWatchValue('arr[i]', '8', '3', '9', on_line=28)
// DexExpectWatchValue('n', '5', on_line=28)
// DexExpectWatchValue('arr[min]', '1', '3', '8', '9', on_line=28)
// DexExpectWatchValue('min', '1', '4', '2', '4', on_line=28)

// DexExpectWatchValue('arr1[0]', '1', on_line=36)
// DexExpectWatchValue('arr1[1]', '1', on_line=36)
// DexExpectWatchValue('arr1[2]', '3', on_line=36)
// DexExpectWatchValue('arr1[3]', '8', on_line=36)
// DexExpectWatchValue('arr1[4]', '9', on_line=36)


// DexExpectStepKind('FUNC_EXTERNAL', 0)
