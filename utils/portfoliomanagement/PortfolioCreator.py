import json
from AlgorithmImports import *
from utils.portfoliomanagement.PortfolioInst import PortfolioInst
from utils.portfoliomanagement.subsystemtypes.QMSubsytem import QMSubsytem

def parse_portfolio(algo: QCAlgorithm, portfolio_name):
    def parse_subsystems(subsystems_list):
        subsystems = []
        for subsystem_dict in subsystems_list:
            if subsystem_dict.get('subsystem_type') == 'Quantmage':
                managers = subsystem_dict.get('managers', [])
                subsystems.append(QMSubsytem(algo, strategy_name=subsystem_dict['name'], managers=managers))
            else:
                # Handle other subsystem types if necessary
                pass
        return subsystems

    def build_portfolio(portfolio_data):
        name = portfolio_data['name']
        
        if portfolio_data['type'] == 'single':
            subsystems = parse_subsystems(portfolio_data['subsystems'])
            return PortfolioInst(algo, portfolio_name=name, subsystems=subsystems, weights=portfolio_data.get('weights'))
        elif portfolio_data['type'] == 'multi':
            child_portfolios = [build_portfolio(child) for child in portfolio_data['child_portfolios']]
            return PortfolioInst(algo, portfolio_name=name, child_portfolios=child_portfolios, weights=portfolio_data.get('weights'))
        else:
            raise ValueError(f"Unknown portfolio type: {portfolio_data['type']}")

    return build_portfolio(json.loads(algo.object_store.read_string(f"portfolios/{portfolio_name}.json"))   ) 

