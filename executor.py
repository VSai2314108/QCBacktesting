# the main method here will function as a bash script and update data before invoke the main.py script
from datetime import datetime
import uuid
from utils.utils.QMUtils import parse_strategy
from utils.utils.DataUpdater import update_data
from utils.utils.PostProcessor import process_orders
import argparse
import os
import glob
import json

def execute_strategy(strategy=None, portfolio=None):
    # UPDATE DATA
    if False:
        parent_dir = os.path.dirname(os.getcwd())
        strategy_dir_path = os.path.join(parent_dir, "storage/qms")
        data_folder = "/Users/vsai23/Workspace/MBQC2/data"

        # Iterate through all JSON files in the directory
        for strategy_file in glob.glob(os.path.join(strategy_dir_path, '*.json')):
            try:
                with open(strategy_file) as file:
                    data = json.load(file)
                _, symbols = parse_strategy(data)
                update_data(symbols, data_folder)
            except Exception as e:
                print(f"Error processing {strategy_file}: {e}")
    
    backtest_name = (portfolio if portfolio else strategy)+"_"+datetime.today().strftime("%Y%m%d_%H%M%S")
    
    # RUN BACKTEST
    # read in the local config.json and add parameters to it
    with open("config.json", "r") as f:
        docker_config = json.load(f)
        docker_config["parameters"]  = {
            "STRATEGY": str(strategy),
            "PORTFOLIO": str(portfolio)
        }  
    
    # write the updated config.json
    with open("config.json", "w") as f:
        json.dump(docker_config, f)
        
    # run the following command in a shell
    commands = [
        "source .venv/bin/activate",
        f"lean backtest . --output ./backtests/{backtest_name} --backtest-name '{backtest_name}'",
    ]
    
    os.system(" && ".join(commands))
    
    # GENERATE CHARTS
    process_orders(f"backtests/{backtest_name}/*-order-events.json")
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute a strategy based on the command line argument.")
    parser.add_argument("--strategy", type=str, required=False, help="The strategy to execute.")
    parser.add_argument("--portfolio", type=str, required=False, help="The portfolio to execute.")
    
    args = parser.parse_args()
    
    execute_strategy(args.strategy, args.portfolio)
    
    