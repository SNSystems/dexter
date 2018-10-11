from dex.command.CommandBase import CommandBase
from dex.dextIR import ValueIR

class DexUnreachable(CommandBase):
  def __init(self):
    super(DexUnreachable, self).__init__()
    pass

  def __call__(self, debugger):
    # If we're ever called, at all, then we're evaluating a line that has
    # been marked as unreachable. Which means a failure.
    vir = ValueIR(expression="Unreachable",
                  value="True", type=None,
                  error_string=None,
                  could_evaluate=True,
                  is_optimized_away=True,
                  is_irretrievable=False)
    return {'DexUnreachable' : vir}
