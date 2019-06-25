from enum import Enum
class ReturnCode(Enum):
   OK = 0
   _ERROR = 1        # Unhandled exceptions result in exit(1) by default.
                     # Usage of _ERROR is discouraged:
                     # If the program cannot run, raise an exception.
                     # If the program runs successfully but the result is
                     # "failure" based on the inputs, return FAIL
   FAIL = 2
