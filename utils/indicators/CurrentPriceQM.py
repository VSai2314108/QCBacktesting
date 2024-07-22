from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class CurrentPriceQM(QM):
    def __init__(self, period):
        # Initialize the base class with the name of the indicator
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        
        # Initialize the current price value
        self.value = 0

    @property
    def IsReady(self):
        # The indicator is always ready since it only needs the current price
        return True

    def update(self, tradebar: TradeBar):
        # Update the current price value with the latest tradebar value
        self.value = tradebar.value
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
