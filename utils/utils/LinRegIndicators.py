from AlgorithmImports import *
import numpy as np
import math

class LinReg(PythonIndicator):
    def __init__(self, period):
        self.Period = period
        self.Slope = None
        self.Intercept = None
        self.Values = []

    @property
    def IsReady(self) -> bool:
        return self.Slope is not None and self.Intercept is not None

    def update(self, input: float):
        self.Values.append(input)
        if len(self.Values) > self.Period:
            del self.Values[0]
            
        if len(self.Values) == self.Period:
            x = np.arange(1, self.Period + 1)
            y = np.array(self.Values)

            slope, intercept = np.polyfit(x, y, 1)
            self.Slope = slope
            self.Intercept = intercept
            
            self.value = intercept + (slope * (self.Period-1))
        
class SlopeIndicator(PythonIndicator):
    def __init__(self, linRegPer, slopePer, longThresh, shortThresh):
        self.linReg: LinReg = LinReg(linRegPer)
        self.slopePer = slopePer
        self.linRegValues = []
        self.linRegPredValues = []
        self.Slope = None
        self.Deg = None
        self.longThresh = longThresh
        self.shortThresh = shortThresh
        self.Signal = None
    
    @property
    def IsReady(self) -> bool:
        return self.Slope is not None
    
    def update(self, input: float):
        self.linReg.update(input)
        if not self.linReg.IsReady:
            return
        
        self.linRegValues.append(self.linReg.Slope)
        self.linRegPredValues.append(self.linReg.value)
        if len(self.linRegValues) > self.slopePer:
            del self.linRegValues[0]

        if len(self.linRegValues) == self.slopePer:
            self.Slope = (self.linRegValues[-1] - self.linRegValues[0])/(self.slopePer-1)
            self.Deg = math.degrees(math.atan(self.Slope))
            self.Signal = 1 if self.Deg > self.longThresh else (-1 if self.Deg < self.shortThresh else 0)