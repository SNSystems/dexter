int calculate_result(const char* buffer)
{


	unsigned capa = 0;
	unsigned lettera = 0;
	unsigned nota = 0;

	while (char c = *buffer++)
	{
		switch (c)
		{
		case 'A':
			capa++; // DexWatch('c', 'capa', 'lettera', 'nota')
			break;
		case 'a':
			lettera++; // DexWatch('c', 'capa', 'lettera', 'nota')
			break;
		default:
			nota++; // DexWatch('c', 'capa', 'lettera', 'nota')
		}
	}

	return (capa + lettera) * nota;
}

int main() {
		const char* buffer = "Any character stream";
		int result = calculate_result(buffer);
		result++;  // DexWatch('result')
		return result;
	}


// DexExpectWatchValue('c',       "'A'", on_line=14)
// DexExpectWatchValue('capa',    '0',   on_line=14)
// DexExpectWatchValue('lettera', '0',   on_line=14)
// DexExpectWatchValue('nota',    '0',   on_line=14)

// DexExpectWatchValue('c',       "'a'",          on_line=17)
// DexExpectWatchValue('capa',    '1',            on_line=17)
// DexExpectWatchValue('lettera', '0', '1', '2',  on_line=17)
// DexExpectWatchValue('nota',    '5', '6', '15', on_line=17)

// DexExpectWatchValue('c', "'n'", "'y'", "' '", "'c'", "'h'", "'r'", "'c'", "'t'", "'e'", "'r'", "' '", "'s'", "'t'", "'r'", "'e'", "'m'", on_line=20)
// DexExpectWatchValue('capa',    '1',                                                                                                      on_line=20)
// DexExpectWatchValue('lettera', '0', '1', '2', '3',                                                                                       on_line=20)
// DexExpectWatchValue('nota',    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15',                     on_line=20)

// DexExpectWatchValue('result', '64', on_line=30)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
