# region imports
from curses.ascii import BS
from AlgorithmImports import *
import json
from typing import List, Tuple, Dict, Union, Optional
import os
from enum import Enum
from utils.utils.StrategyParsing import parse_strategy
# endregion

# region mappings
from utils.indicators import CumulativeReturnQM, ExponentialMovingAverageQM, MonthNumberQM, MovingAverageQM, MovingAverageReturnsQM, RelativeStrengthIndexQM, CurrentPriceQM, MaxDrawdownQM, VolatilityQM
mapping = {
    "CumulativeReturn": CumulativeReturnQM,
    "MovingAverage": MovingAverageQM,
    "RelativeStrengthIndex": RelativeStrengthIndexQM,
    "CurrentPrice": CurrentPriceQM,
    "MaxDrawdown": MaxDrawdownQM,
    "Month": MonthNumberQM,
    "ExponentialMovingAverage": ExponentialMovingAverageQM,
    "MaxDrawdown": MaxDrawdownQM,
    "MovingAverageReturns": MovingAverageReturnsQM,
    "Volatility": VolatilityQM
}
# endregion

# STRATEGY IMPORTS
from utils.utils.Strategy import BSMR, UNCORRELATEDBONDS1, NEOBETABALLER_4_1

class IncantationType(Enum):
    SWITCH = 1
    WEIGHTED = 2
    TICKER = 3
    FILTERED = 4
    IFELSE = 5

class QCBacktesting(QCAlgorithm):

    def initialize(self):
        # Set the strategy parameters
        self.set_start_date(2023, 7, 22)  # Set Start Date
        self.set_end_date(2024, 7, 22)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash
        self.set_warm_up(20)  # Set Warm Up Period
        self.settings.liquidate_enabled = True
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)
        self.settings.free_portfolio_value_percentage = 0.05

        
        self.strategy = json.loads(NEOBETABALLER_4_1)
        
        # Parse strategy file to get indicators and symbols
        self.indicator_list, self.symbol_list = parse_strategy(self.strategy)
        self.symbol_list = set(self.symbol_list)
        
        # Add the Month indicator and Volatility,20 indicator for their uses
        self.indicator_list.extend([("Volatility", 20)])
        self.symbol_list.add("SPY")
        
        self.indicators = {}  # Stored as dict with the following key-value pairs: {indicator_name_ticker_window: indicator_object}
        
        # Add equities and initialize indicators
        for symbol in self.symbol_list:
            security = self.add_equity(symbol, Resolution.DAILY)
            security.set_fee_model(ConstantFeeModel(0))

            for indicator_name, period in self.indicator_list:
                indicator_instance = mapping[indicator_name](period)
                
                indicator_key = f"{indicator_name}_{symbol}_{period}"
                self.indicators[indicator_key] = indicator_instance

                # Register and warm up the indicator
                self.register_indicator(symbol, indicator_instance, Resolution.DAILY)
                self.warm_up_indicator(symbol, indicator_instance)
        
        # Add non-equity specific indicators
        self.non_equity_indicators = [("Month", 0)]
        for indicator_name, period in self.non_equity_indicators:
            indicator_instance = mapping[indicator_name](period)
            indicator_key = f"{indicator_name}_{period}"
            self.indicators[indicator_key] = indicator_instance
            self.register_indicator("SPY", indicator_instance, Resolution.DAILY)
            self.warm_up_indicator("SPY", indicator_instance)

        self.schedule.on(self.date_rules.every_day(), self.time_rules.after_market_open("SPY", 5), self.run_evaluate_daily)

    def run_evaluate_daily(self):
        # Call evaluate_strategy with the main strategy incantation
        output_weights = self.evaluate_strategy(self.strategy["incantation"])

        # sum the weights for repeated tickers
        ticker_weights = {}
        for ticker, w in output_weights:
            if ticker in ticker_weights:
                ticker_weights[ticker] += w
            else:
                ticker_weights[ticker] = w
        
        # validate the weights
        # total_weight = sum(ticker_weights.values())
        # while total_weight > 1:
        #     # reduce all weights by 1%
        #     for k in ticker_weights:
        #         ticker_weights[k] = ticker_weights[k] * 0.99
        #     total_weight = sum(ticker_weights.values())

        # convert to list of PortfolioTarget objects
        ticker_weights = [PortfolioTarget(k,v) for k, v in ticker_weights.items()]
        
        self.set_holdings(ticker_weights, liquidate_existing_holdings=True)

    def evaluate_strategy(self, incantation: Optional[Dict[str, dict]] = None, cur_weight: float = 1) -> List[float]:
        if not incantation:
            return []        
        incantation_type = incantation.get("incantation_type")
        incantation_enum = IncantationType[incantation_type.upper()]

        if incantation_enum == IncantationType.SWITCH:
           return self.switch_strategy(incantation, cur_weight)
        elif incantation_enum == IncantationType.WEIGHTED:
            return self.weighted_strategy(incantation, cur_weight)
        elif incantation_enum == IncantationType.TICKER:
            return self.ticker_strategy(incantation, cur_weight)
        elif incantation_enum == IncantationType.FILTERED:
            return self.filtered_strategy(incantation, cur_weight)
        elif incantation_enum == IncantationType.IFELSE:
            return self.if_else_strategy(incantation, cur_weight)
        
        return []

    def switch_strategy(self, incantation: Dict[str, dict], cur_weight: float) -> float:
        conditions = incantation.get("conditions")
        cond_results = [self.evaluate_condition(condition) for condition in conditions]
        incantation_index = len(conditions) - sum(cond_results)
        result_incantation = incantation.get("incantations")[incantation_index]
        return self.evaluate_strategy(result_incantation, cur_weight)

    def weighted_strategy(self, incantation: Dict[str, dict], cur_weight: float) -> float:
        weight_type = incantation.get("type")
        incantations = incantation.get("incantations")
        if weight_type == "Equal":
            new_weight = cur_weight / (len(incantations)*1.0)
            outputs = [self.evaluate_strategy(incantation, new_weight) for incantation in incantations]
            outputs = [item for sublist in outputs for item in sublist]
            return outputs
        elif weight_type == "Custom":
            weights = incantation.get("weights")
            outputs = []
            for i, incantation in enumerate(incantations):
                outputs.append(self.evaluate_strategy(incantation, cur_weight * (weights[i]/100.0)))
            outputs = [item for sublist in outputs for item in sublist]
            return outputs
        elif weight_type == "InverseVolatility": # implement this eventually
            volatility_window = incantation.get("inverse_volatility_window")
            outputs = [self.evaluate_strategy(incantation, cur_weight) for incantation in incantations]
            
            # calculate inverse volatility for each sublist
            inverse_volatilities = []
            for output in outputs:
                temp_inverse_vol_sum = 0
                for ticker, weight in output: # not sure if weight is used here
                    volatility_key = f"Volatility_{ticker}_{volatility_window}"
                    temp_inverse_vol_sum += 1/self.indicators.get(volatility_key).value
                inverse_volatilities.append(temp_inverse_vol_sum)
            
            # calculate weights
            total_inverse_volatility = sum(inverse_volatilities)
            for output, inverse_volatility in zip(outputs, inverse_volatilities):
                for i in range(len(output)):
                    output[i] = (output[i][0], output[i][1] * (inverse_volatility / total_inverse_volatility))
            
            return outputs
                
    def ticker_strategy(self, incantation: Dict[str, dict], cur_weight: float) -> float:
        return [(incantation.get("symbol"), cur_weight)]

    def filtered_strategy(self, incantation: Dict[str, dict], cur_weight: float) -> float:
        sort_indicator = incantation.get("sort_indicator").get("type")
        sort_indicator_window = incantation.get("sort_indicator").get("window")
        mx = not incantation.get("bottom")
        count = incantation.get("count")
        incantations = incantation.get("incantations")
        
        outputs = [self.evaluate_strategy(incantation, cur_weight) for incantation in incantations]
        
        # evaluate the sort indicator for all tickers in each sublist and computer weighted average, then sort
        outputs_with_indicator = [] #([(ticker,weight), ...], indicator_value)
        for output in outputs:
            temp_val = 0
            temp_weights = 0
            for ticker, weight in output:
                sort_indicator_key = f"{sort_indicator}_{ticker}_{sort_indicator_window}"
                sort_indicator_value = self.indicators.get(sort_indicator_key).value
                temp_val += sort_indicator_value
                temp_weights += weight
            outputs_with_indicator.append((output, (temp_val / temp_weights)))
        
        outputs_with_indicator.sort(key=lambda x: x[1], reverse=mx)
        outputs_with_indicator = outputs_with_indicator[:count]
        
        outputs = [output for output, _ in outputs_with_indicator]
        
        # apply the weighting methods to the outputs
        weight_type = incantation.get("weight_type")
        inverse_volatility_window = incantation.get("inverse_volatility_window")
        weights = incantation.get("weights")
        if weight_type == "Equal":
            outputs = [(item[0], item[1]*(1/count)) for sublist in outputs for item in sublist]
            return outputs
        elif weight_type == "Custom":
            for sublist in outputs:
                for i in range(len(sublist)):
                    sublist[i] = (sublist[i][0], sublist[i][1] * (weights[i]/100.0))
            outputs = [item for sublist in outputs for item in sublist]
            return outputs
        elif weight_type == "InverseVolatility":
            inverse_volatilities = []
            for output in outputs:
                temp_inverse_vol_sum = 0
                for ticker, weight in output:
                    volatility_key = f"Volatility_{ticker}_{inverse_volatility_window}"
                    temp_inverse_vol_sum += 1/self.indicators.get(volatility_key).value
                inverse_volatilities.append(temp_inverse_vol_sum)
            
            # calculate weights
            total_inverse_volatility = sum(inverse_volatilities)
            for output, inverse_volatility in zip(outputs, inverse_volatilities):
                for i in range(len(output)):
                    output[i] = (output[i][0], output[i][1] * (inverse_volatility / total_inverse_volatility))
            
            outputs = [item for sublist in outputs for item in sublist]
            return outputs
        
            

    def if_else_strategy(self, incantation: Dict[str, dict], cur_weight: float) -> float:
        condition = incantation.get("condition")
        if self.evaluate_condition(condition):
            then_incantation = incantation.get("then_incantation")
            return self.evaluate_strategy(then_incantation)
        else:
            else_incantation = incantation.get("else_incantation")
            return self.evaluate_strategy(else_incantation)

    def evaluate_condition(self, condition: Optional[Dict[str, dict]]):
        condition_type = condition.get("condition_type")
        if condition_type == "AllOf":
            return all([self.evaluate_condition(c) for c in condition.get("conditions")])
        elif condition_type == "AnyOf":
            return any([self.evaluate_condition(c) for c in condition.get("conditions")])
        elif condition_type == "SingleCondition":
            lh_value, rh_value = 0, 0
            if condition["type"] == "Month":
                lh_ticker = condition["lh_ticker_symbol"]
                lh_value = self.indicators.get("Month_0").value
                rh_value = condition["rh_value"]
            else:
                lh_indicator = condition["lh_indicator"]["type"]
                lh_period = condition["lh_indicator"].get("window", None)
                lh_ticker = condition["lh_ticker_symbol"]
                lh_value = self.indicators.get(f"{lh_indicator}_{lh_ticker}_{lh_period}").value
                if condition["type"] == "BothIndicators":
                    rh_indicator = condition["rh_indicator"]["type"]
                    rh_period = condition["rh_indicator"].get("window", None)
                    rh_ticker = condition["rh_ticker_symbol"]
                    rh_value = self.indicators.get(f"{rh_indicator}_{rh_ticker}_{rh_period}").value
                elif condition["type"] == "IndicatorAndNumber":
                    rh_value = condition["rh_value"]
                else:
                    raise ValueError("Invalid condition type")
                    
            # evaluate
            if condition.get("greater_than"):
                return lh_value > (rh_value + condition.get("rh_bias", 0))
            else:
                return lh_value <= (rh_value + condition.get("rh_bias", 0))

    def on_data(self, data: slice):
        pass