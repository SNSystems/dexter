This is a version of the fibonacci test that copies the value of the passed-by-
reference variable 'total' into a local variable 'localtotal' prior to the
loop and then copies the value of 'localtotal' back into 'total' subsequent
to the loop.

This should avoid the issue described in https://llvm.org/PR37682 where
the store to 'total' is hoisted out of the loop so the value in the watch view 
is not updated.
