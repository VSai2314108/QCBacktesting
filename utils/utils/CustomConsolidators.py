from AlgorithmImports import *
from datetime import time, timedelta, datetime

class ShorterDayConsolidator(TradeBarConsolidator):
    def __init__(self):
        # initialize the base class with calendar info
        self.after_time = time(15,55)
        super().__init__(self._consolidation_period)
    
    def update(self, data):
        if self.after_time:
            if data.Time.time() >= self.after_time:
                return
        super().update(data)
    
    def _consolidation_period(self, dt: datetime) -> CalendarInfo:
        start_time = time(9, 30)
        period = timedelta(hours=6, minutes=25)
        end_time = self.after_time
        
        start = dt.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        
        if dt.time() >= end_time:
            start += timedelta(days=1)
        start = start.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        
        return CalendarInfo(start, period)