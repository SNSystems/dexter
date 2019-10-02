# A GDB interface wrapper for Dexter. Note that this code touches GDBs python
# API, and thus may or may not be GPL3.
#
# GDB does not provide a mechanism to be loaded inside some other process,
# instead it allows a python script to be run inside of itself. Dexter operates
# assuming the former is true; we have to fit the two together. To do this,
# we have gdb load a mini module (in the gdb_trampoline file), then connect
# the dexter process with gdb through pythons rpyc RPC module. Aside from setup,
# as far as this (Gdb) module is aware, it gets a "gdb" object that acts like
# gdb.
#
# This module is not intended to be portable to Windows -- use a Windows
# debugger or that.

# Load the rpyc module.
try:
  import rpyc
except ImportError:
  rpyc = None

# Try to load sched_yield for yielding; if it isn't available, define one that
# is a no-op. This leads to busy waiting.
try:
  from os import sched_yield # pylint: disable=no-name-in-module
except ImportError:
  def sched_yield():
    pass

# Import a monotonic clock timer.
try:
  from time import monotonic as m_clock # pylint: disable=no-name-in-module
except ImportError:
  from time import clock as m_clock

import os
import sys
import shutil
from subprocess import CalledProcessError, check_output, STDOUT, Popen

from dex.dextIR import FrameIR, LocIR, StepIR, StopReason, ValueIR
from dex.dextIR import ProgramState, StackFrame, SourceLocation
from dex.debugger.DebuggerBase import DebuggerBase
from dex.utils.Exceptions import DebuggerException, LoadDebuggerException

# Timeout numbers for gdb starting and connecting to it -- these were
# selected with little consideration, but seem OK.
GDB_START_TIME = 2.0
GDB_CONNECT_TIME = 1.0

class Gdb(DebuggerBase):
  def __init__(self, context, *args):
    self.progname = 'gdb'
    self.proc = None      # Popen object for gdb subprocess.
    self.rpyc_obj = None  # rpyc connection object.
    self.gdb = None       # Handle to remote processes gdb object.
    self.pyfile_path = '{}/gt.py'.format(context.working_directory.path)
    self.sockdir = '{}/sock'.format(context.working_directory.path)
    self.sockpath = '{}/foot'.format(self.sockdir)
    super(Gdb, self).__init__(context, *args)

  @classmethod
  def get_name(cls):
    return 'gdb'

  @classmethod
  def get_option_name(cls):
    return 'gdb'

  @property
  def version(self):
    lines = check_output([self.progname,  '--version'], stderr = STDOUT)
    lines = lines.decode('utf-8')
    line = lines.split('\n')[0]
    verstr = line.split(' ')[-1].rstrip()
    return verstr

  def _load_interface(self):
    if rpyc is None:
      raise LoadDebuggerException('Could not import rpyc: can\'t speak to gdb')
    try:
      check_output([self.progname,  '--version'], stderr = STDOUT)
    except CalledProcessError as e:
      raise LoadDebuggerException(str(e), sys.exc_info())
    except OSError as e:
      raise LoadDebuggerException(
            '{} [{}]'.format(e.strerror, self.progname), sys.exc_info())

  def _custom_init(self):
    # Copy gdb trampoline code into working directory, with .py extension.
    # Spawn a version of gdb that runs it, and from this process connect to
    # the rpyc socket.
    trampoline_path = '{}/gdb_trampoline'.format(os.path.dirname(__file__))
    shutil.copyfile(trampoline_path, self.pyfile_path)

    src_cmd = 'source {}'.format(self.pyfile_path)
    devnull = open('/dev/null', 'w')
    self.proc = Popen([self.progname, '-ex', src_cmd],
                       stdin=devnull, stdout=devnull, stderr=devnull)

    self.wait_for_socket()
    self.connect_to_socket()
    self.gdb = self.rpyc_obj.root.gdb
    self.rpyc_obj.root.register_stuff()
    self.gdb.execute('file {}'.format(self.context.options.executable))

  def wait_for_socket(self):
    # Problem: we can't make any progress until gdb connects back to us,
    # or it croaks, and that might take some period of time.
    starttime = m_clock()
    res = None
    while m_clock() < starttime + GDB_START_TIME:
      try:
        res = os.stat(self.sockpath)
      except OSError:
        pass

      if res is not None:
        break
      if self.proc.poll() is not None:
        raise DebuggerException("GDB terminated before connecting to dexter")

      sched_yield() # Don't busy wait

    if res is None:
      # Then we timed out
      try:
        self.proc.kill()
      except OSError:
        pass # No such process -> no problemo
      raise DebuggerException("GDB did not start up promptly")

  def connect_to_socket(self):
    starttime = m_clock()
    while m_clock() < starttime + GDB_CONNECT_TIME:
      try:
        self.rpyc_obj = rpyc.utils.factory.unix_connect(self.sockpath)
      except ConnectionRefusedError: # pylint: disable=undefined-variable
        pass
      if self.rpyc_obj is not None:
        break

      sched_yield() # Don't busy wait

    if self.rpyc_obj is None:
      raise DebuggerException("GDB did not connect to dexter promptly")

  def _custom_exit(self):
    if self.rpyc_obj is not None:
      self.rpyc_obj.close()
      self.rpyc_obj = None
    self.gdb = None

    if self.proc is not None:
      try:
        self.proc.kill()
      except OSError:
        pass # No such process -> no problemo
      self.proc = None

    def wrapunlink(p):
      try:
        os.unlink(p)
      except OSError:
        pass
    wrapunlink(self.pyfile_path)
    wrapunlink(self.sockpath)
    wrapunlink(self.sockdir)

  @property
  def is_running(self):
    # If debugged process is free-running, we wouldn't be able to tell, as
    # everything would block. Just ping the remote process to confirm that
    # it isn't running right now.
    self.rpyc_obj.root.ping()
    return False

  @property
  def is_finished(self):
    if self.gdb.selected_inferior().threads() == tuple():
      return True

    # GDB conveniently gives us a line after main returns
    if str(self.gdb.newest_frame().function()) in self.frames_below_main:
      return True

    return False

  @property
  def frames_below_main(self):
    return ['__scrt_common_main_seh', '__libc_start_main']

  def step(self):
    self.rpyc_obj.root.events.clear()
    self.rpyc_obj.root.events.append("step")
    self.gdb.execute("step")

  def go(self):
    self.gdb.execute("continue")

  def launch(self):
    self.gdb.execute("run")

  def add_breakpoint(self, file_, line):
    file_ = os.path.basename(file_)
    self.gdb.Breakpoint('{}:{}'.format(file_, line))

  def clear_breakpoints(self):
    bps = self.gdb.breakpoints()
    if bps is None:
      return
    for x in bps:
      x.delete()

  def unwrap_gdb_value(self, val):
    if val.type.code == self.gdb.TYPE_CODE_INT:
      # Apparently wrong in gdb? (should be TYPE_CODE_CHAR?)
      if str(val.type) == 'char':
        return "'{}'".format(chr(val))
      return int(val)
    if val.type.code == self.gdb.TYPE_CODE_BOOL:
      return "true" if bool(val) else "false"
    if val.type.code == self.gdb.TYPE_CODE_STRUCT:
      return str(val)
    if val.type.code == self.gdb.TYPE_CODE_FLT:
      return str(val)
    elif val.type.code == self.gdb.TYPE_CODE_REF:
      # Dereference the reference.
      return self.unwrap_gdb_value(val.referenced_value())
    elif val.type.code == self.gdb.TYPE_CODE_ARRAY:
      # Staple together each element
      thelen = int(val.type.sizeof / val.type.target().sizeof)
      items = [str(self.unwrap_gdb_value(val[x])) for x in range(thelen)]
      return '{' + ', '.join(items) + '}'
    else:
      #raise DebuggerException('Unrecognized gdb type {}'.format(str(val.type)))
      return ''

  def evaluate_expression(self, expression, frame_idx = 0):
    # XXX -- select correct stack frame?
    expr = expression
    error = False
    optout = False
    value = 0
    thetype = None
    try:
      expr_value = self.gdb.parse_and_eval(expr)
      thetype = expr_value.type.name

      if expr_value.is_optimized_out:
        optout = True
      else:
        value = self.unwrap_gdb_value(expr_value)
    except DebuggerException:
      raise
    except Exception as e: # pylint: disable=broad-except
      error = True

    return ValueIR(
        expression = expr,
        value = str(value),
        type_name = thetype,
        error_string = '',
        could_evaluate = not error,
        is_optimized_away = optout,
        is_irretrievable = error)

  @staticmethod
  def translate_stop_reason(reason):
    if reason == "exited":
      return StopReason.PROGRAM_EXIT
    elif reason == "break":
      return StopReason.BREAKPOINT
    elif reason == "step":
      return StopReason.STEP
    return StopReason.OTHER

  def get_step_info(self):
    # Get the last event we look at.
    if len(self.rpyc_obj.root.events) > 0:
      evt = self.rpyc_obj.root.events[-1]
      self.rpyc_obj.root.clear_events()
      reason = self.translate_stop_reason(evt)
    else:
      reason = StopReason.OTHER

    # Build up frame information.
    frames = []
    state_frames = []
    curframe = self.gdb.newest_frame()
    assert curframe is not None
    while curframe is not None:
      frames.append(curframe)
      curframe = curframe.older()

    firs = []
    for i, x in enumerate(frames):
      function = x.function()

      if function in self.frames_below_main:
        break

      symtab = x.find_sal().symtab
      if symtab is not None:
        line = x.find_sal().line
        file_ = symtab.fullname()
        file_ = self._sanitize_function_name(file_)
      else:
        file_ = None
        line = 0

      loc_dict = {
          'path': str(file_),
          'lineno': int(line),
          'column': 0 # XXX gdb has no columns?
      }

      loc = LocIR(**loc_dict)

      # XXX is_inlined, not clear that gdb presents this?
      fr = FrameIR(function = str(function), is_inlined = False, loc = loc)
      firs.append(fr)

      state_frame = StackFrame(function=fr.function,
                               is_inlined=fr.is_inlined,
                               location=SourceLocation(**loc_dict),
                               watches={})
      for expr in map(
          lambda watch, idx=i: self.evaluate_expression(watch, idx),
          self.watches):
          state_frame.watches[expr.expression] = expr
      state_frames.append(state_frame)

    return StepIR(step_index = self.step_index, frames = firs,
                  stop_reason = reason,
                  program_state = ProgramState(state_frames))
