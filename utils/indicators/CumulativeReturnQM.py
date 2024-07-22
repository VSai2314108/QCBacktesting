from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class CumulativeReturnQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial cumulative return value
        self.closes: RollingWindow = RollingWindow[float](period+1)
        self.cumulative_return = 0
        self.temp_value = None

    @property
    def IsReady(self):
        return self.closes.is_ready

    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if not self.IsReady:
            return False
        
        self.cumulative_return = (self.closes[0] - self.closes[self.closes.size-1]) / self.closes[self.closes.size-1]
        self.value = self.cumulative_return * 100  # Convert to percentage
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        cur_pre_close = input.value
        temp_cumulative_return = (cur_pre_close - self.closes[self.closes.size-2]) / self.closes[self.closes.size-2]
        self.temp_value = temp_cumulative_return * 100  # Convert to percentage

# Example usage
# period = 14  # Example period
# cumulative_return_indicator = CumulativeReturnQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# cumulative_return_indicator.update(tradebar)
