from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM
import numpy as np

class VolatilityQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial Volatility value
        self.closes: RollingWindow = RollingWindow[float](period+1)
        self.returns: RollingWindow = RollingWindow[float](period)
        self.temp_value = None

    @property
    def IsReady(self):
        return self.closes.is_ready and self.returns.is_ready

    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if self.closes.count > 1:
            ret = (self.closes[0] - self.closes[1]) / self.closes[1]
            self.returns.add(ret)
        
        if not self.IsReady:
            return False
        
        self.value = np.std(list(self.returns)) * 100  # Convert to percentage
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        temp_closes = [input.value] + list(self.closes)
        temp_returns = []
        
        for i in range(len(temp_closes) - 1):
            ret = (temp_closes[i] - temp_closes[i + 1]) / temp_closes[i + 1]
            temp_returns.append(ret)
        
        self.temp_value = np.std(temp_returns) * 100  # Convert to percentage

# Example usage
# period = 14  # Example period
# volatility_indicator = VolatilityQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# volatility_indicator.update(tradebar)
