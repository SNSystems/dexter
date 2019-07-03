from ctypes import *

E_NOINTERFACE = 0x80004002 - 0x100000000
E_FAIL = 0x80004005 - 0x100000000
E_EINVAL = 0x80070057 - 0x100000000
E_INTERNALEXCEPTION = 0x80040205 - 0x100000000
S_FALSE = 1

# This doesn't fit into any convenient category
DEBUG_ANY_ID = 0xFFFFFFFF

class WinError(Exception):
  def __init__(self, msg, hstatus):
    self.hstatus = hstatus
    super(WinError, self).__init__(msg)

def aborter(res, msg, legit=[]):
  if res != 0 and res not in legit:
    if res < 0:
      res += 0x100000000
    msg = '{:08X} : {}'.format(res, msg)
    raise WinError(msg, res)

IID_Data4_Type = c_ubyte * 8

class IID(Structure):
  _fields_ = [
      ("Data1", c_uint),
      ("Data2", c_ushort),
      ("Data3", c_ushort),
      ("Data4", IID_Data4_Type)
  ]

c_ulong_p = POINTER(c_ulong)
c_ulong64_p = POINTER(c_ulonglong)
