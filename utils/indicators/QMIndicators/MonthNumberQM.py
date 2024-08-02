from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMIndicators.QMParent import QM

class MonthNumberQM(QM):
    def __init__(self, period):
        # Initialize the base class with the name of the indicator
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        self.warm_up_period = 1
        self.value = None

    @property
    def IsReady(self):
        # The indicator is always ready since it only needs the current price
        return not self.value is None

    def update(self, tradebar: TradeBar):
        # Update the current price value with the latest tradebar value
        self.value = tradebar.end_time.month
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True

    def temp_update(self, input: TradeBar):
        # Temporary update to simulate the current price
        self.temp_value = input.value

# Example usage
# current_price_indicator = CurrentPriceQM()
# tradebar = TradeBar(time, open, high, low, close, volume)  # Example tradebar
# current_price_indicator.update(tradebar)
