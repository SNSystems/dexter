// Purpose:
//      Check that parsing bad commands gives a useful error.
//          - Syntax error (misplaced ',') over multiple lines
//      Check directives are in check.txt to prevent dexter reading any embedded
//      commands.
//
// RUN: dexter.py test --builder clang --debugger lldb --cflags "-O0 -g" -v \
// RUN:     -- %S \
// RUN:     | FileCheck "%S/check.txt" --match-full-lines --strict-whitespace

int main(){
    return 0;
}

/*
DexExpectWatchValue(
    ,'a', 3, 3, 3, 3, on_line=0)
*/