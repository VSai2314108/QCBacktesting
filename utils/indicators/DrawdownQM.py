from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class DrawdownQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial drawdown value
        self.all_time_high = float('-inf')
        self.closes = []
        self.temp_value = None
        
    @property
    def IsReady(self):
        return len(self.closes) > 0

    def update(self, tradebar: TradeBar):
        self.closes.append(tradebar.value)
        
        if tradebar.value > self.all_time_high:
            self.all_time_high = tradebar.value
        
        self.value = self.calculate_drawdown(tradebar.value)
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def calculate_drawdown(self, current_price):
        if self.all_time_high == float('-inf'):
            return 0
        return (self.all_time_high - current_price) / self.all_time_high

    def temp_update(self, input: TradeBar):
        if not self.IsReady:
            return
        
        # Calculate temporary drawdown for a new tradebar
        temp_all_time_high = max(self.all_time_high, input.value)
        temp_drawdown = (temp_all_time_high - input.value) / temp_all_time_high
        
        self.temp_value = temp_drawdown

# Example usage
# period = 14  # Example period, though it's not directly used in this case
# drawdown_indicator = DrawdownQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# drawdown_indicator.update(tradebar)
