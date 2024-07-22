from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class MovingAverageQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial Moving Average value
        self.closes: RollingWindow = RollingWindow[float](period)
        self.moving_average = 0
        self.temp_value = None

    @property
    def IsReady(self):
        return self.closes.is_ready

    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if not self.IsReady:
            return False
        
        self.moving_average = sum(self.closes) / self.closes.count
        self.value = self.moving_average
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        temp_closes = [input.value] + list(self.closes)[:self.closes.count-1]
        
        temp_moving_average = sum(temp_closes) / len(temp_closes)
        
        self.temp_value = temp_moving_average

# Example usage
# period = 14  # Example period
# moving_average_indicator = MovingAverageQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# moving_average_indicator.update(tradebar)
