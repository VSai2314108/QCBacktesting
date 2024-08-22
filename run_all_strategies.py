import os
import glob
import json
import sys
from executor import execute_strategy

def create_portfolio_json(strategy_name: str, output_dir: str):
    portfolio = {
        "name": strategy_name,
        "type": "single",
        "weight_type": "equal",
        "subsystems": [
            {
                "name": strategy_name,
                "subsystem_type": "Quantmage"
            }
        ],
        "weights": []
    }
    
    file_name = strategy_name.replace(" ", "_") + ".json"
    portfolio_file = os.path.join(output_dir, file_name)
    with open(portfolio_file, 'w') as f:
        json.dump(portfolio, f, indent=4)
    
    return portfolio_file

def setup_logging(strategy_name: str):
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, f"{strategy_name.replace(' ', '_')}.log")
    return open(log_file, 'w')

def run_all_strategies():
    parent_dir = os.path.dirname((os.getcwd()))
    strategy_dir_path = os.path.join(parent_dir, "storage", "qms")
    portfolio_dir_path = os.path.join(parent_dir, "storage", "portfolios")
    
    print(f"Output directory: {portfolio_dir_path}")
    print(f"Strategy directory: {strategy_dir_path}")
    print(f"Portfolio directory: {portfolio_dir_path}")
    
    os.makedirs(portfolio_dir_path, exist_ok=True)
    
    for strategy_file in glob.glob(os.path.join(strategy_dir_path, '*.json')):
        try:
            strategy_name = os.path.splitext(os.path.basename(strategy_file))[0]
            strategy_name = strategy_name.replace("_", " ")
            
            log_file = setup_logging(strategy_name)
            sys.stdout = log_file
            sys.stderr = log_file
            
            print(f"Processing strategy: {strategy_name}")
            
            portfolio_file = create_portfolio_json(strategy_name, portfolio_dir_path)
            portfolio_name = os.path.splitext(os.path.basename(portfolio_file))[0]
            
            print(f"Executing strategy: {strategy_name} with portfolio: {portfolio_name}")
            
            execute_strategy(strategy=strategy_name, portfolio=portfolio_name)
            print(f"Successfully executed strategy: {strategy_name}")
        except Exception as e:
            print(f"Error executing strategy {strategy_name}: {e}")
            print(f"Execution status: FAILED")
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            log_file.close()

if __name__ == "__main__":
    run_all_strategies()