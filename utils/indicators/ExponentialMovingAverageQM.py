from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class ExponentialMovingAverageQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.period = period
        self.value = 0  # Initial EMA value
        self.closes: RollingWindow = RollingWindow[float](period)
        self.ema = None  # EMA will be initialized after the first period closes
        self.temp_value = None

    @property
    def IsReady(self):
        return self.closes.is_ready

    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if not self.IsReady:
            return False
        
        if self.ema is None:
            # Initialize EMA with the simple moving average of the first period
            self.ema = sum(self.closes) / self.closes.count
        else:
            # Calculate the multiplier (W)
            W = 2 / (self.period + 1)
            # Calculate the EMA
            self.ema = self.ema * (1 - W) + tradebar.value * W

        self.value = self.ema
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        # Calculate temporary EMA for a new tradebar
        W = 2 / (self.period + 1)
        if self.ema is None:
            temp_ema = sum(list(self.closes)) / len(self.closes)
        else:
            temp_ema = self.ema * (1 - W) + input.value * W
        
        self.temp_value = temp_ema

# Example usage
# period = 14  # Example period
# moving_average_indicator = ExponentialMovingAverageQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# moving_average_indicator.update(tradebar)
