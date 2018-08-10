#!/usr/bin/env bash
set -e

for INDEX in {SOURCE_INDEXES}
do
  CFLAGS=$(eval echo "\$COMPILER_OPTIONS_$INDEX")
  SRCFILE=$(eval echo "\$SOURCE_FILE_$INDEX")
  OBJFILE=$(eval echo "\$OBJECT_FILE_$INDEX")
  clang++ -std=gnu++11 -c $CFLAGS $SRCFILE -o $OBJFILE
done

clang++ {LINKER_OPTIONS} {OBJECT_FILES} -o {EXECUTABLE_FILE}

