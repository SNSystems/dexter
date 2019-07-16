# Dexter commands

* [DexExpectProgramState](Commands.md#DexExpectProgramState)
* [DexExpectStepKind](Commands.md#DexExpectStepKind)
* [DexExpectStepOrder](Commands.md#DexExpectStepOrder)
* [DexExpectWatchValue](Commands.md#DexExpectWatchValue)
* [DexUnreachable](Commands.md#DexUnreachable)
* [DexWatch](Commands.md#DexWatch)

---
## DexExpectProgramState
    DexExpectProgramState(state [,**times])

    Args:
        state (dict): { 'frames': [
                        {
                          # StackFrame #
                          'function': name (str),
                          'is_inlined': bool,
                          'location': {
                            # SourceLocation #
                            'lineno': int,
                            'path': str,
                            'column': int,
                          },
                          'watches': {
                            expr (str): value (str),
                          },
                        }
                      ]}

    Keyword args:
        times (int): Minumum number of ime this state pattern is expected to be
            seen. Defaults to 1. Can be 0.

### Description
Expect to see a given program `state` a certain numer of `times`.

When matching expected against reported states:
* Omitted fields in `StackFrame` and `SourceLocation` dictionaries are ignored.
* The state match fails if the results of each `expr` in `watches`
does not match the given `value`.


### Heuristic
[TODO]


---
## DexExpectStepKind
    DexExpectStepKind(kind, times)

    Args:
      kind (str): Expected step kind.
      times (int): Expected number of encounters.

### Description
Expect to see a particular step `kind` a number of `times` while stepping
through the program.

`kind` must be one of: `'FUNC'`, `'FUNC_EXTERNAL'`, `'FUNC_UNKNOWN'`,
`'FORWARD'`, `'SAME'`, `'BACKWARD'`, `'UNKNOWN'`.

### Heuristic
[TODO]


---
## DexExpectStepOrder
    DexExpectStepOrder(index)

    Args:
      index (int): Position in sequence of DexExpectStepOrder commands

### Description
Expect the line this command is found on to be stepped on before all other
DexExpectStepOrder commands with a greater `index` argument.

### Heuristic
[TODO]


---
## DexExpectWatchValue
    DexExpectWatchValue(expr, *values[,**from_line=1][,**to_line=Max]
                        [,**on_line])

    Args:
        expr (str): C++ expression to evaluate.

    Arg list:
        values (str): At least one expected value. NOTE: string type.

    Keyword args:
        from_line (int): Evaluate the expression from this line. Defaults to 1.
        to_line (int): Evaluate the expression to this line. Defaults to end of
            source.
        on_line (int): Only evaluate the expression on this line. If provided,
            this overrides from_line and to_line.

### Description
Expect the C++ expression `expr` to evaluate to the list of `values`
sequentially.

### Heuristic
[TODO]


---
## DexUnreachable
    DexUnreachable()

### Description
Expect the source line this is found on will never be stepped on to.

### Heuristic
[TODO]


----
## DexLabel
    DexLabel(name)

    Args:
        name (str): A unique name for this line.

### Description
Name the line this command is found on. Line names can be referenced by other
commands expecting line number arguments.
For example, `DexExpectWatchValues(..., on_line='my_line_name')`.

### Heuristic
This command does not contribute to the heuristic score.


---
## DexWatch
    DexWatch(*expressions)

    Arg list:
        expressions (str): C++ `expression` to evaluate on this line.

### Description
Evaluate the `expressions` on the line this command is found on. Use in
combination with `annotate-expected-values` to generate `DexExpectWatchValues`
commands for this source file.

### Heuristic
This command is only used to help generate `DexExpectWatchValues`. It does not
contribute to the heuristic score.
