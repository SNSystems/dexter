#!/usr/bin/env bash

dexterloc=$1
shift;

cflags=""
marker=0
args=()

# Inhale dexter options before '--', append anything afterwards to cflags,
# feed back into dexter.

while test "$#" != 0; do
  case $1 in
    "--cflags")
      # --cflags on dexter cmdline -> store for later manipulation
      if test "$#" -lt 2; then
        echo "Missing argument to --cflags" >&2
        exit 1
      fi
      cflags="$2";
      shift
      shift
      ;;
    --)
      # Prepare to bail
      marker=1
      shift;
      ;;
    *)
      # A dexter argument -- just put it in the array of them
      args+=($1)
      shift
      ;;
  esac
  if test "$marker" = 1; then
    break;
  fi
done

# Expand all subsequent arguments into the string for cflags
cflags+=" $@";

exec $dexterloc "${args[@]}" --cflags "${cflags}"
