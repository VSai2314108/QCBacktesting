from datetime import datetime
from AlgorithmImports import *
import pandas as pd
import json
import os

from src.portfoliomanagement.Subsystem import Subsystem
from src.utils.QMUtils import *

class QMSubsytem(Subsystem):
    """
    Represents a subsystem within the Quantmage format
    """
    def __init__(self, algo: QCAlgorithm, strategy_name: str, managers: List[str] = None):
        Subsystem.__init__(self, algo)
        self.strategy_name = strategy_name
        self.strategy_def = json.loads(algo.object_store.read_string(f"qms/{strategy_name}.json"))
        self.indicators, self.symbols = parse_strategy(self.strategy_def)
        self.strategy_insights : Dict[datetime: List[PortfolioTarget]] = {}
        self.managers = managers
        # initialize managers from str names eventually, all will have a run method
    
    def run_manager(self, allocations: List[Tuple[str, float]]):
        # pass the allocation to the manager who will modify it and pass it back
        pass

    def evaluate(self) -> List[Tuple[str, float]]:
        allocations = evaluate_strategy(self.algo, self.strategy_def["incantation"])
        self.portfolio_tracker[self.algo.time] = dict(allocations)
        return allocations
    
    def write(self, tag=""):
        tag = (tag+"/"+self.strategy_name).replace(" ", "_")
        file_name = f"/Results/{tag}/{self.strategy_name}.csv"
        os.makedirs(f"/Results/{tag}", exist_ok=True)
        dataframe = pd.DataFrame.from_dict(self.portfolio_tracker).T
        # fill in missing values with 0
        dataframe = dataframe.fillna(0)
        dataframe.index.name = "Date"
        dataframe.to_csv(file_name)
        