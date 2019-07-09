# DexVerify
## Contents
1. Introduction
2. Motivation
3. Theory
4. Quick reference

## 1. Introduction
A DexVerify command takes the form `DexVerify(p: Proposition)`. It will verify
that the proposition `p` is true. The most basic proposition, an atomic
proposition, expresses the expected state of the program at a given point in
time, or `True` or `False`.

For example, if you wanted to verify that at a given point in time the variable
`a` is equal to `5`, you may write (1):
```
DexVerify(Expect('a', '5'))
```

In this example, it just so happens that the "given point in time" is the first
step that the debugger takes (2). This is not a very useful verification
because we could be stepping through pre-main startup code.

If you want to check that eventually a local variable `a` is `5` you'd write:
```
DexVerify(Eventually(Expect('a', '5')))
```

`Eventually` is a temporal operator. **Temporal** operators work over **time**.
This one is easy to work with. simply, `Eventually(p)` means that p must become
true at some point during program execution.

`Eventually(p)` is defined as `Until(True, p)` (see the
[source](dex/command/commands/LTD/public/CompositeOperators.py)).
It's easy to explain how this works if we take a look at `Until(p, q)`.
`Until` and `Weak` (see the Quick reference) are used to define all other
temporal operators. All operators are exposed as functions so the formulae
read in Polish, or 'prefix', notation.

`Until(p, q)` means that `q` must hold in the future, and **until** then `p`
must hold.

Looking at `Eventually(p)` again then; `Until(True, p)` can be translated to
"`p` must hold in the future, and until then, `True` must hold". `True` *is*
always `True` so you could instead just say "`p` must hold in the future".

Temporal operators are very useful but are not a catch-all solution. What if
you want to say eventually `a == 5` and eventually `b == 1`? It's pretty much
as easy as writing that. This is where boolean connectives come in:
```
DexVerify(And(Eventually(Expect('a', '5')), Eventually(Expect('b', '1'))))
```

This formula doesn't impose any ordering on the `Expect` propositions.
If you want to say that `b == 1` at some point in the future *after*
`a == 5` you'd write:
```
DexVerify(Eventually(And(Expect('a', 5), Eventually(Expect('b', 1)))))
```

For more examples have a look in dexter/examples/LTD. Please be aware that the
prefix "xfail_" indicates that running that test should result in a failure.

## 2. Motivation

[TODO] Write this section


## 3. Thoery
The DexVerify command formulae are based on Linear Temporal Logic (LTL).
The standard definition of LTL is as follows (modified from [this](https://www.win.tue.nl/~jschmalt/teaching/2IX20/reader_software_specification_ch_9.pdf) source):

```
p ::= a  |  p /\ p  |  !p  |  Xp |  p U p
```

Where:
* `a` is an atomic proposition
* `p` represents a valid LTL formula
* `X` denotes the ”next” operator (3)
* `U` denotes the ”until” operator
* `!` denotes negation
* `/\` denotes logical "and"


Usual boolean connectives can be derived:
```
!(p /\ q) == p \/ q   // (disjunciton)
!p \/ q == p --> q    // (implication)
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
There are others, e.g. Weak(W) and Release(R) and more.

[This](http://www.lsv.fr/~gastin/ltl2ba/index.php) website is a fantastic
resource for viewing your LTL formula as a Büchi automaton.

Operator precedence doesn't matter for our case because all operators
are exposed as functions, but for infix LTL:
1. Unary operators
2. Binary temporal
3. Binary boolean


## 4. Quick reference
### Atomic propositions
#### Boolean
```
True
False
```
Not strictly "atomic propositions" in terms of LTL theory.

#### Expect
```
Expect(p, q)
```
Debugger C++ expression `p` must evaluate to value `q`.

### Boolean functions

#### And

#### Or

#### Not

### Temporal functions

#### Until
```
Until(p, q)
```
`q` must eventually hold and until then `p` must hold.<br/>
LTL definition: `U` &#8801; Until &#8801; for `0 <= i` where `q` holds `p` holds
for `0 <= k < i`.

#### Weak
```
Weak(p, q)
```
`p` must hold so long as `q` does not.<br/>
LTL definition: `W` &#8801; Weak &#8801; Weak until &#8801; for `0 <= i` where `q` holds `p` holds for `0 <= k < i`, or, if `q` never holds, `0 <= k`.

#### Eventually
```
Eventually(p)
```
`p` must eventually hold.<br/>
LTL definition: `F` &#8801; Finally &#8801; Eventually &#8801; Future &#8801;
`True U p`

#### Release
```
Release(p, q)
```
`p` must eventually hold and up to and including that time `q` must hold.
NOTE: Operand order and keyword *including*.<br/>
LTL definition: `R` &#8801; Release &#8801; `q U (q /\ p)`

#### Henceforth
```
Henceforth(p)
```
`p` must hold from now onwards.<br/>
LTL definition: `G` &#8801; Globally &#8801; `False R p`

---
### Examples
[TODO] Add examples after coming up with some syntactic sugar for the common
patterns.


### [TODO] / notes
1. The Expect syntax will not look anything like this.
2. Makes sense for the first step to be stepping into main -- discuss with team.
3. Next is not currently and may never be implemented -- no use case yet.
