from dex.command.CommandBase import CommandBase
from dex.dextIR import ValueIR

class DexExpectStepOrder(CommandBase):
    def __init__(self, *args):
        if not args:
            raise TypeError('Need at least one order number')

        self.sequence = [int(x) for x in args]
        super(DexExpectStepOrder, self).__init__()

    @staticmethod
    def get_name():
        return __class__.__name__

    def eval(self, debugger):
        step_info = debugger.get_step_info()
        loc = step_info.current_location
        return {'DexExpectStepOrder': ValueIR(expression=str(loc.lineno),
                      value=str(debugger.step_index), type_name=None,
                      error_string=None,
                      could_evaluate=True,
                      is_optimized_away=True,
                      is_irretrievable=False)}
