from AlgorithmImports import *
from datetime import datetime
from utils.indicators.QMParent import QM

class RelativeStrengthIndexQM(QM):
    def __init__(self, period):
        QM.__init__(self, self.__class__.__qualname__ + "_" + str(period), period)
        # self.name = self.indicator_name
        # self.time = datetime.min
        
        self.value = 50  # Neutral RSI value before it's ready
        self.closes: RollingWindow = RollingWindow[float](period+1)
        self.avg_gain = None
        self.avg_loss = None
        self.temp_value = None
        

    @property
    def IsReady(self):
        if not self.closes.is_ready:
            return False
        return True
        
    def update(self, tradebar: TradeBar):
        self.closes.add(tradebar.value)
        
        if not self.IsReady:
            return False
        elif self.closes.is_ready and self.avg_gain is None: # initialize
            gain = 0
            loss = 0
            for i in range(0, self.period):
                change = self.closes[i] - self.closes[i+1]
                if change > 0:
                    gain+=change
                else:
                    loss-=change
            
            self.avg_gain = gain/self.period
            self.avg_loss = loss/self.period
        else:
            change = self.closes[0] - self.closes[1]
            if change > 0:
                self.avg_gain = (self.avg_gain * (self.period - 1) + change) / self.period
                self.avg_loss = (self.avg_loss * (self.period - 1)) / self.period
            else:
                self.avg_gain = (self.avg_gain * (self.period - 1)) / self.period
                self.avg_loss = (self.avg_loss * (self.period - 1) - change) / self.period
        
        self.value = 100 if self.avg_loss == 0 else 100 - (100 / (1 + (self.avg_gain / self.avg_loss)))
        self.temp_value = self.value
        self.values.append(self.value)
        
        return True
     
    def temp_update(self, input: TradeBar):
        if not self.closes.is_ready:
            return
        
        cur_pre_close = input.value
        change = cur_pre_close - self.closes[0]
        avg_gain,avg_loss = None, None
        if change > 0:
            avg_gain = (self.avg_gain * (self.period - 1) + change) / self.period
            avg_loss = (self.avg_loss * (self.period - 1)) / self.period
        else:
            avg_gain = (self.avg_gain * (self.period - 1)) / self.period
            avg_loss = (self.avg_loss * (self.period - 1) - change) / self.period
        
        self.temp_value = 100 if avg_loss == 0 else 100 - (100 / (1 + (avg_gain / avg_loss)))