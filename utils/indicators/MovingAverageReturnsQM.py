from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class MovingAverageReturnsQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        self.value = 0  # Initial Moving Average of Returns value
        self.returns: RollingWindow = RollingWindow[float](period)
        self.prices: RollingWindow = RollingWindow[float](period + 1)  # Window size is period + 1 to store period returns
        self.temp_value = None

    @property
    def IsReady(self):
        return self.returns.is_ready

    def update(self, tradebar: TradeBar):
        self.prices.add(tradebar.close)
        
        if len(self.prices) > 1:
            # Calculate the return
            current_return = (self.prices[0] - self.prices[1]) / self.prices[1]
            self.returns.add(current_return)
        
        if not self.IsReady:
            return False
        
        # Calculate the moving average of returns
        self.value = sum(self.returns) / self.returns.count
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if len(self.prices) < 1 or not self.returns.is_ready:
            return
        
        # Calculate the temporary return
        temp_return = (input.close - self.prices[0]) / self.prices[0]
        
        temp_returns = [temp_return] + list(self.returns)[:self.returns.count-1]
        
        temp_moving_average_returns = sum(temp_returns) / len(temp_returns)
        
        self.temp_value = temp_moving_average_returns

# Example usage
# period = 14  # Example period
# moving_average_returns_indicator = MovingAverageReturnsQM(period)
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# moving_average_returns_indicator.update(tradebar)
