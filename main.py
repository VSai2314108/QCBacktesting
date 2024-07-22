# region imports
from curses.ascii import BS
from AlgorithmImports import *
import json
from typing import List, Tuple, Dict, Union, Optional
import os
from utils.utils.StrategyParsing import parse_strategy
# endregion

# region mappings
from utils.indicators import CumulativeReturnQM, MovingAverageQM, RelativeStrengthIndexQM, CurrentPriceQM, MaxDrawdownQM
mapping = {
    "CumulativeReturn": CumulativeReturnQM,
    "MovingAverage": MovingAverageQM,
    "RelativeStrengthIndex": RelativeStrengthIndexQM,
    "CurrentPrice": CurrentPriceQM,
    "MaxDrawdown": MaxDrawdownQM
}
# endregion

# STRATEGY IMPORTS
from utils.utils.Strategy import BSMR
            
class QCBacktesting(QCAlgorithm):

    def initialize(self):
        # Set the strategy parameters
        self.set_start_date(2022, 10, 7)  # Set Start Date
        self.set_end_date(2023, 10, 11)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash
        # self.settings.daily_precise_end_time = True

        self.strat_name: str = "BSMR"
        self.path: str = os.path.join("qm", f"{self.strat_name}.json")
        # with open(self.path, 'r') as f:
        #     data = json.load(self.path)
        self.strategy: Dict[str, Dict] = json.loads(BSMR)
        
        # Parse strategy file to get indicators and symbols
        self.indicator_list, self.symbol_list = parse_strategy(self.strategy)

        self.indicators = {}  # Stored as dict with the following key-value pairs: {indicator_name_ticker_window: indicator_object}
        
        # Add equities and initialize indicators
        for symbol in self.symbol_list:
            self.add_equity(symbol, Resolution.DAILY)

            for indicator_name, period in self.indicator_list:
                indicator_instance = mapping[indicator_name](period)
                
                indicator_key = f"{indicator_name}_{symbol}_{period}"
                self.indicators[indicator_key] = indicator_instance

                # Register and warm up the indicator
                self.register_indicator(symbol, indicator_instance, Resolution.DAILY)
                self.warm_up_indicator(symbol, indicator_instance)
        self.schedule.on(self.date_rules.every_day(), self.time_rules.before_market_close("SPY", 4), lambda: self.evaluate_strategy(self.strategy["incantation"]))
        
    def evaluate_condition(self, condition: Optional[Dict[str, dict]]):
        lh_indicator = condition["lh_indicator"]["type"]
        lh_period = condition["lh_indicator"].get("window", None)
        lh_ticker = condition["lh_ticker_symbol"]
        lh_value = self.indicators.get(f"{lh_indicator}_{lh_ticker}_{lh_period}").value

        # determine if it is BothIndicator or IndicatorAndNumber
        if condition["type"] == "BothIndicator":
            rh_indicator = condition["rh_indicator"]["type"]
            rh_period = condition["rh_indicator"].get("window", None)
            rh_ticker = condition["rh_ticker_symbol"]
            rh_value = self.indicators.get(f"{rh_indicator}_{rh_ticker}_{rh_period}").value
        else:
            rh_value = condition["rh_value"]        
        
        if condition.get("greater_than"):
            return lh_value > rh_value + condition.get("rh_bias", 0)
        else:
            return lh_value < rh_value + condition.get("rh_bias", 0)
    
    def evaluate_strategy(self, incantation: Optional[Dict[str, dict]] = None):
        if not incantation:
            return
        condition = incantation.get("condition")
        if condition and self.evaluate_condition(condition):
            then_incantation = incantation.get("then_incantation")
            if then_incantation and then_incantation.get("incantation_type") == "Ticker":
                symbol = then_incantation.get("symbol")
                self.set_holdings(symbol, 1, liquidate_existing_holdings=True)
            else:
                self.evaluate_strategy(then_incantation)
        else:
            else_incantation = incantation.get("else_incantation")
            self.evaluate_strategy(else_incantation)
    
    
    def on_data(self, data: slice):
        pass