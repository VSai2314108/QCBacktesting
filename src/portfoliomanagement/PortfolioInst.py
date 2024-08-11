from AlgorithmImports import *
from src.portfoliomanagement.Subsystem import Subsystem
from src.portfoliomanagement.subsystemtypes.QMSubsytem import QMSubsytem
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
    
    def write(self, tag: str = ""):
        tag = tag+"/"+self.portfolio_name if tag else self.portfolio_name
        if self.type == "single":
            for subsystem in self.subsystems:
                subsystem.write(tag)
        else:
            for child_portfolio in self.child_portfolios:
                child_portfolio.write(tag)
    
    def write_portfolio(self, tag: str = ""):
        if self.type == "single":
            subsystem_allocation_list = [pd.DataFrame.from_dict(subsystem.portfolio_tracker).T for subsystem in self.subsystems]
            
            # get all index values from the dataframes and add missing rows with 0 values
            index_values = set()
            for df in subsystem_allocation_list:
                index_values.update(df.index)
            for i, df in enumerate(subsystem_allocation_list):
                missing_rows = index_values - set(df.index)
                for row in missing_rows:
                    subsystem_allocation_list[i].loc[row] = pd.Series(0, index=df.columns)
            
            # create a dict of index: num of systems with at least one allocation
            index_count = {}
            for df in subsystem_allocation_list:
                for index, row in df.iterrows():
                    if row.sum() > 0:
                        index_count[index] = index_count.get(index, 0) + 1
            
            # determine which weighting system to use 
            if self.weights:
                weighting_system = self.weights
                # multiply each dataframe by the corresponding weight
                for i, df in enumerate(subsystem_allocation_list):
                    subsystem_allocation_list[i] = df.multiply(weighting_system[i])
            else:
                # for each key in index divide by the number of systems with at least one allocation
                for index in index_count:
                    for i, df in enumerate(subsystem_allocation_list):
                        subsystem_allocation_list[i].loc[index] = df.loc[index] / index_count[index]
            
            # sum the dataframes
            combined_allocation = pd.DataFrame()
            for df in subsystem_allocation_list:
                combined_allocation = combined_allocation.add(df, fill_value=0)
            
            # write the combined allocation to a csv
            tag = (tag+"/"+self.portfolio_name).replace(" ", "_")
            file_name = f"/Results/{tag}/{self.portfolio_name}.csv"
            os.makedirs(f"/Results/{tag}", exist_ok=True)
            combined_allocation = combined_allocation.fillna(0)
            combined_allocation.index.name = "Date"
            combined_allocation.to_csv(file_name)
            
            # write all the subsystems to csv
            self.write(tag)
            
            # return the combined allocation for upstream use
            return combined_allocation
        else:
            # update tag
            tag = (tag+"/"+self.portfolio_name).replace(" ", "_")

            # gather all the child portfolio allocations
            child_portfolio_allocation_list = [child_portfolio.write_portfolio(tag) for child_portfolio in self.child_portfolios]
            
            # compute weights
            if self.weights:
                weights = self.weights
            else:
                weights = [1/len(self.child_portfolios) for _ in self.child_portfolios] # we dont track active vs inactive portfolios
            
            # multiply each dataframe by the corresponding weight
            for i, df in enumerate(child_portfolio_allocation_list):
                child_portfolio_allocation_list[i] = df.multiply(weights[i])
                
            # sum the dataframes
            combined_allocation = pd.DataFrame()
            for df in child_portfolio_allocation_list:
                combined_allocation = combined_allocation.add(df, fill_value=0)
                
            # write the combined allocation to a csv
            file_name = f"/Results/{tag}/{self.portfolio_name}.csv"
            os.makedirs(f"/Results/{tag}", exist_ok=True)
            combined_allocation = combined_allocation.fillna(0)
            combined_allocation.index.name = "Date"
            combined_allocation.to_csv(file_name)
            
            return combined_allocation        