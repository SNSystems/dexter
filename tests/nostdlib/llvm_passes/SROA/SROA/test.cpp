// RUN: %dexter
struct SROAThis {
  SROAThis(int n_a, int n_b, int n_c, int n_d)
    : a(n_a), b(n_b), c(n_c), d(n_d){}

  int a, b, c, d;
};
struct SROAThis2 {
  SROAThis2(int n_a, int n_b, int n_c, int n_d)
    : a(n_a), b(n_b), c(n_c), d(n_d){}

  int a, b, c, d;
};

int doesSroaStuff(SROAThis & aggr, SROAThis2 & aggr2) {
  aggr.a  += 1;                             // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr.b  += 2;                             // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr2.c += 3;                             // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr2.d += 4;                             // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr2.c += aggr.a + aggr.b;               // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr2.d += aggr.a + aggr.b;               // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr.b  += aggr2.c + aggr2.d;             // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  aggr.a  += aggr.b  + aggr2.c + aggr2.d;   // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
  return aggr.a;                            // DexWatch('aggr.a', 'aggr.b', 'aggr2.c', 'aggr2.d')
}

int main(int argc, const char ** argv) {
  SROAThis aggr(argc, argc, argc, argc);
  SROAThis2 aggr2(argc, argc, argc, argc);

  auto a = doesSroaStuff(aggr, aggr2);

  return a;
}

// DexExpectWatchValue('aggr.a',  '1', '2', '43', from_line=16, to_line=24)
// DexExpectWatchValue('aggr.b',  '1', '3', '22', from_line=16, to_line=24)
// DexExpectWatchValue('aggr2.c', '1', '4', '9',  from_line=16, to_line=24)
// DexExpectWatchValue('aggr2.d', '1', '5', '10', from_line=16, to_line=24)
