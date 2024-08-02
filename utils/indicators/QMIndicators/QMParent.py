from AlgorithmImports import *

class QM(PythonIndicator):
    def __init__(self, indicator_name, period):
        super().__init__()
        self.indicator_name: str = indicator_name
        self.values: list[float] = []
        self.period: int = period
        self.warm_up_period = period+10
    
    def update(self, tradebar: TradeBar):
        return
    
    def temp_update(self, input: TradeBar):
        return

    