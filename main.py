# region imports
from AlgorithmImports import *
import json
from enum import Enum
from utils.portfoliomanagement.subsystemtypes.QMSubsytem import QMSubsytem
from utils.utils.QMUtils import parse_strategy
from utils.utils.QMUtils import evaluate_strategy
from utils.portfoliomanagement.PortfolioCreator import parse_portfolio
from utils.portfoliomanagement.PortfolioInst import PortfolioInst
# endregion

# region mappings
from utils.indicators.QMIndicators import CumulativeReturnQM, ExponentialMovingAverageQM, MonthNumberQM, MovingAverageQM, MovingAverageReturnsQM, RelativeStrengthIndexQM, CurrentPriceQM, MaxDrawdownQM, VolatilityQM
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

from utils.utils.QMUtils import *
# endregion

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
        self.parameters: dict = self.get_parameters()
        
        # set up for the strategy or portfolio 
        self.strategy_name = self.parameters["STRATEGY"]
        self.portfolio_name = self.parameters["PORTFOLIO"]
        self.portfolio_backtest = True if self.portfolio_name!="None" else False
        
        if self.strategy_name!="None":
            self.strategyInst: QMSubsytem = QMSubsytem(self, self.strategy_name)
            self.indicator_list, self.symbol_list = list(self.strategyInst.indicators), list(self.strategyInst.symbols)

        if self.portfolio!="None":
            self.portfolioInst: PortfolioInst = parse_portfolio(self, self.portfolio_name)
            self.indicator_list, self.symbol_list = list(self.portfolioInst.indicators), list(self.portfolioInst.symbols)
        
        # Add the Month indicator and Volatility,20 indicator for their uses
        self.indicator_list.extend([("Volatility", 20)])
        self.symbol_list.append("SPY")
        
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
        output_weights = self.portfolioInst.evaluate() if self.portfolio_backtest else self.strategyInst.evaluate()

        # sum the weights for repeated tickers
        ticker_weights = {}
        for ticker, w in output_weights:
            if ticker in ticker_weights:
                ticker_weights[ticker] += w
            else:
                ticker_weights[ticker] = w

        # convert to list of PortfolioTarget objects
        ticker_weights = [PortfolioTarget(k,v) for k, v in ticker_weights.items()]
        
        self.set_holdings(ticker_weights, liquidate_existing_holdings=True)

    def on_data(self, data: slice):
        pass
    
    def on_end_of_algorithm(self):
       if self.portfolio_backtest:
            self.portfolioInst.write()