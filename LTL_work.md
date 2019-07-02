# LTL-Like language for DExTer
## LTL (Linear Temporal Logic)

The standard definition of LTL is as follows (modified from [this](https://www.win.tue.nl/~jschmalt/teaching/2IX20/reader_software_specification_ch_9.pdf) source):

```
p ::= a  |  p /\ p  |  !p  |  Xp |  p U p
```

Where:
* `a` is an atomic proposition
* `p` represents a valid LTL formula
* `X` denotes the ”next” operator
* `U` denotes the ”until” operator
* `!` denotes negation
* `/\` denotes logical "and"


Usual boolean connectives can be derived:
```
!(p /\ q) == p \/ q   // (disjunciton): i.e. OR
!p \/ q == p --> q    // (implication):
```

From the syntax, we define the following:
```
p \/ !p == True
!True == False
```

Further temporal operators can be derived:
```
F p == true U p  // p will hold at some point in the Future.
```
There are others, e.g. Weak(W) and Release(R) and more, but I haven't
encountered a scenario in dexter where we need them yet. We may also remove the
Next operator.

Operator precedence:
1. Unary operators
2. Binary temporal
3. Binary boolean
---

## LTD (Linear Temporal Dexter commands)
We expose the LTL operators as functions. This makes the formulae easy to parse
because the functions will map directly to python like the existing DexCommands.

Associativity is still important for reasons outliend later. Temporal operators
are right associative and boolean connectives are left associative. e.g.
```
p U true U q == p U (true U q) == p U ( F q )
```
This reads "q must hold at some point, and p must hold at some point prior".

### LTD functors
```
Proposition
  // Atomic propositions
  ExpectValues(Proposition)
    vars: list
    values: list
  ExpectStack(Proposition)
    frames: list
  ExpectState(ExpectValues, ExpectStack)

  // Unary operators
  Not(Proposition)
    prop: Proposition
  Next(Proposition)

  // Binary boolean operators
  BinaryBoolean(Proposition)
    Or(BinaryBoolean)
      list: Proposition
    And(BinaryBoolean)
      list: Proposition

  // Binary temporal operators
  BinaryTemporal(Proposition)
    Until(BinaryTemporal)
      list: Proposition
```
The binary operators all take a list argument. This is syntactic sugar for a
chained sequence of operators. Operator associativity is important because is
applies when resolving a chain like this.
```
Until(x, y, z) == Until(x, Until(y, z))
```
Which Reads "Z must hold at some point, until then y must hold, and until then x
must hold."

### Examples
Dexter/FoldBranchToCommonDest/test.cpp
```
int g_a = 0;
int run_loop();
int do_something();

static bool condition(int c)
{
  return c > 4; // DexWatch("c")
}
int main()
{
  int x = 0;
  while (run_loop())
  {
    if (condition(++x))
      break;
    do_something();
  }

  return g_a;
}

// DexExpectWatchValue("c", "1", "2", "3", "4", "5", on_line=7)

/* v --- LTD --- v
DexVerify(
  Until(
    Future(ExpectState({lines: [7], vars:[c], values:[1]})),
    Future(ExpectState({lines: [7], vars:[c], values:[2]})),
    Future(ExpectState({lines: [7], vars:[c], values:[3]})),
    Future(ExpectState({lines: [7], vars:[c], values:[4]})),
    Future(ExpectState({lines: [7], vars:[c], values:[5]}))
  )
)
*/
```
debuginfo-tests/asan-blocks.c
```
void b();
struct S {
  int a[8];
};

int f(struct S s, unsigned i) {
  // DEBUGGER: break 17
  // DEBUGGER: r
  // DEBUGGER: p s
  // CHECK: a = ([0] = 0, [1] = 1, [2] = 2, [3] = 3, [4] = 4, [5] = 5, [6] = 6, [7] = 7)
  return s.a[i];
}

int main(int argc, const char **argv) {
  struct S s = {{0, 1, 2, 3, 4, 5, 6, 7}};
  if (f(s, 4) == 4) {
    // DEBUGGER: break 27
    // DEBUGGER: c
    // DEBUGGER: p s
    // CHECK: a = ([0] = 0, [1] = 1, [2] = 2, [3] = 3, [4] = 4, [5] = 5, [6] = 6, [7] = 7)
    b();
  }
  return 0;
}

void c() {}

void b() {
  // DEBUGGER: break 40
  // DEBUGGER: c
  // DEBUGGER: p x
  // CHECK: 42
  __block int x = 42;
  c();
}

/* v --- LTD --- v
DexVerify(
  Future(
    Until(
      ExpectState({stack: [f, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [17]}),
      ExpectState({stack: [main, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [27]}),
      Future(ExpectState({stack: [b, *], vars: [x], values: [42], lines: [40]}))
    )
  )
)
*/
```

[todo] Show verbocity of Dexter/fibonacci with LTD :(

### LTD Suggestions

Renaming operators or patterns of operators may be useful. Subject to future
changes, I like these substitutions (remember that binary operator functions
take a list of operands):
```
Until    -> Consecutively
Future   -> Eventually (This is the formal name anyway)
And      -> All
Or       -> Any
```

Then instead of:
```
DexVerify(
  Future(
    Until(
      ExpectState({stack: [f, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [17]}),
      ExpectState({stack: [main, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [27]}),
      Future(ExpectState({stack: [b, *], vars: [x], values: [42], lines: [40]}))
    )
  )
)
```
we could write:
```
DexVerify(
  Eventually(
    Consecutively(
      ExpectState({stack: [f, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [17]}),
      ExpectState({stack: [main, *], vars: [s.a[0], s.a[1], s.a[2], <etc>], values: [0, 1, 2, <etc>], lines: [27]}),
      Eventually(ExpectState({stack: [b, *], vars: [x], values: [42], lines: [40]}))
    )
  )
)
```
We can have syntactic sugar too. If we say that a list of propositions that are
**Eventually** true, **Consecutively**, are listed **Sequentially** then we can
change the following example (which I've updated with the syntax proposed above)
from this:
```
DexVerify(
  Consecutively(
    Eventually(ExpectState({lines: [7], vars:[c], values:[1]})),
    Eventually(ExpectState({lines: [7], vars:[c], values:[2]})),
    Eventually(ExpectState({lines: [7], vars:[c], values:[3]})),
    Eventually(ExpectState({lines: [7], vars:[c], values:[4]})),
    Eventually(ExpectState({lines: [7], vars:[c], values:[5]}))
  )
)
```
to this:
```
DexVerify(
  Sequentially(
    ExpectState({lines: [7], vars:[c], values:[1]}),
    ExpectState({lines: [7], vars:[c], values:[2]}),
    ExpectState({lines: [7], vars:[c], values:[3]}),
    ExpectState({lines: [7], vars:[c], values:[4]}),
    ExpectState({lines: [7], vars:[c], values:[5]})
  )
)
```
