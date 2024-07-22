# the main method here will function as a bash script and update data before invoke the main.py script
from Strategy import BSMR
from StrategyParsing import parse_strategy
from DataUpdater import update_data
import os
import json
if __name__ == "__main__":
    data = json.loads(BSMR)
    indicators, symbols = parse_strategy(data)
    data_folder = "/Users/vsai23/Workspace/MBQC2/data"
    update_data(symbols, data_folder)
    
    # run the following command in a shell
    commands = [
        "source .venv/bin/activate",
        "exec lean backtest"
    ]
    
    os.system(" && ".join(commands))
    
    