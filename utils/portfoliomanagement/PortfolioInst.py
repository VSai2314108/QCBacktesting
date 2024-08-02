from AlgorithmImports import *
from utils.portfoliomanagement.Subsystem import Subsystem
from utils.portfoliomanagement.subsystemtypes.QMSubsytem import QMSubsytem
import pandas as pd
import os
class PortfolioInst:
    """
    Represents a portfolio of subsystems or child portfolios for backtesting.
    Is not aware of the subsystem managers, only aware of the subsystems executed trades. 

    Args:
        algo (QCAlgorithm): The algorithm instance.
        portfolio_name (str): The name of the portfolio.
        subsystems (List[Subsystem], optional): List of subsystems in the portfolio. Defaults to None.
        child_portfolios (List[Portfolio], optional): List of child portfolios. Defaults to None.
        weights (List, optional): List of weights for subsystems or child portfolios. Defaults to None.

    Attributes:
        algo (QCAlgorithm): The algorithm instance.
        portfolio_name (str): The name of the portfolio.
        subsystems (List[Subsystem]): List of subsystems in the portfolio.
        child_portfolios (List[Portfolio]): List of child portfolios.
        weights (List): List of weights for subsystems or child portfolios.
        type (str): Type of the portfolio, either "single" or "multiple".

    Methods:
        evaluate(): Evaluates the portfolio and returns a list of (str, float) tuples.

    """
    mappings = {
        "Quantmage": QMSubsytem,
    }

    def __init__(self, algo: QCAlgorithm, portfolio_name: str, subsystems: List[Subsystem] = None, child_portfolios: List[Portfolio] = None, weights: List = None):
        self.algo: QCAlgorithm = algo
        self.portfolio_name = portfolio_name
        self.subsystems = subsystems
        self.child_portfolios = child_portfolios
        self.weights = weights
        self.type = "single" if subsystems else "multiple"
        self.indicators, self.symbols = self.gather()
    
    def gather(self):
        indicators = set()
        symbols = set()
        if self.type == "single":
            for subsystem in self.subsystems:
                subsystem_indicators, subsystem_symbols = subsystem.indicators, subsystem.symbols
                indicators.update(subsystem_indicators)
                symbols.update(subsystem_symbols)
        else:
            for child_portfolio in self.child_portfolios:
                child_indicators, child_symbols = child_portfolio.indicators, child_portfolio.symbols
                indicators.update(child_indicators)
                symbols.update(child_symbols)
        return indicators, symbols
        
    
    def evaluate(self) -> List[Tuple[str, float]]:
        """
        Evaluates the portfolio and returns a list of (str, float) tuples.

        Returns:
            List[Tuple[str, float]]: List of (str, float) tuples representing the evaluation results.

        """
        # for readibility - does the same thing either way
        if self.type == "single":
            subsystem_outputs = [subsystem.evaluate() for subsystem in self.subsystems]
            outputs = []
            if self.weights:
                for subsystem_output, weight in zip(subsystem_outputs, self.weights):
                    for output in subsystem_output:
                        outputs.append((output[0], output[1] * weight))
            else:
                weight = sum([1 for subsystem_output in subsystem_outputs if subsystem_output != []])
                if weight == 0:
                    return []
                weight = 1/weight
                for subsystem_output in subsystem_outputs:
                    for output in subsystem_output:
                        outputs.append((output[0], output[1] * weight))
            return outputs
        else:
            portfolio_outputs = [child_portfolio.evaluate() for child_portfolio in self.child_portfolios]
            # 1 more level of nesting than the single case
            outputs = []
            if self.weights:
                for portfolio_output, weight in zip(portfolio_outputs, self.weights):
                    for output in portfolio_output:
                        outputs.append((output[0], output[1] * weight))
            else:
                weight = sum([1 for portfolio_output in portfolio_outputs if portfolio_output != []])
                if weight == 0:
                    return []
                weight = 1/weight
                for portfolio_output in portfolio_outputs:
                    for output in portfolio_output:
                        outputs.append((output[0], output[1] * weight))
            return outputs
    
    def write(self, tag: str = None):
        tag = tag+"/"+self.portfolio_name if tag else self.portfolio_name
        if self.type == "single":
            for subsystem in self.subsystems:
                subsystem.write(tag)
        else:
            for child_portfolio in self.child_portfolios:
                child_portfolio.write(tag)
    
    def write_portfolio(self, tag: str = None):
        # pass merges the subsystem data for single portfolios, and the child portfolio data for multi portfolios
        pass                     
        