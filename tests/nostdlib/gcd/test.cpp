#ifdef _MSC_VER
# define DEX_NOINLINE __declspec(noinline)
#else
# define DEX_NOINLINE __attribute__((__noinline__))
#endif

DEX_NOINLINE
int GCD(int lhs, int rhs)
{
	if (rhs == 0)
		return lhs;
	return GCD(rhs, lhs % rhs);
}

int main()
{
	return GCD(111, 259);
}

/*
DexExpectProgramState({
	'frames': [
		{
			'location': {
				'lineno': 11
			},
			'local_vars': {
				'lhs': '37', 'rhs': '0'
			}
		},
		{
			'local_vars': {
				'lhs': '111', 'rhs': '37'
			}
		},
		{
			'local_vars': {
				'lhs': '259', 'rhs': '111'
			}
		},
		{
			'local_vars': {
				'lhs': '111', 'rhs': '259'
			}
		}
	]
})
*/
