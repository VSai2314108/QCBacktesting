from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class MaxDrawdownQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial Max Drawdown value
        self.closes: RollingWindow = RollingWindow[float](period+1)
        self.max_drawdown = 0
        self.temp_value = None

    @property
    def IsReady(self):
        return self.closes.is_ready

    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if not self.IsReady:
            return False
        
        max_drawdown = 0
        for i in range(self.closes.count - 1):
            for j in range(i + 1, self.closes.count):
                drawdown = (self.closes[i] - self.closes[j]) / self.closes[j]
                if drawdown < max_drawdown:
                    max_drawdown = drawdown
        
        self.max_drawdown = max_drawdown
        self.value = abs(self.max_drawdown * 100)  # Convert to percentage
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        temp_closes = [input.value] + list(self.closes)[:self.closes.count-1]
        
        temp_max_drawdown = 0
        for i in range(len(temp_closes) - 1):
            for j in range(i + 1, len(temp_closes)):
                drawdown = (temp_closes[i] - temp_closes[j]) / temp_closes[j]
                if drawdown < temp_max_drawdown:
                    temp_max_drawdown = drawdown
        
        self.temp_value = abs(temp_max_drawdown) * 100  # Convert to percentage

# Example usage
# period = 14  # Example period
# max_drawdown_indicator = MaxDrawdownQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# max_drawdown_indicator.update(tradebar)
