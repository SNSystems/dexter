// RUN: %dexter

struct iterator {
  int index_;
  iterator(int index) : index_(index) {}
  bool operator!=(iterator const &rhs) const { return index_ != rhs.index_; }
  int operator*() { return index_; }
  int operator++() { return index_++; }
};

template <int BEGIN, int END> struct range {
  iterator begin() const { return iterator(BEGIN); }
  iterator end() const { return iterator(END); }
};

int main(int argc, char **) {
  range<0, 5> list;
  int total = 0;
  for (volatile auto elem : list)
    total += elem * argc; // DexWatch('total', 'elem', 'argc')
  return total;
}

// DexExpectWatchValue('elem', '0', '1', '2', '3', '4', on_line=18)
// DexExpectWatchValue('total', '0', '1', '3', '6', on_line=18)
// DexExpectWatchValue('argc', '1', on_line=18)

// DexExpectStepKind('FUNC_EXTERNAL', 0)
