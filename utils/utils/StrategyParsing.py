from typing import List, Tuple, Dict, Union

from numpy import sort

def parse_strategy(strategy: Dict[str, Union[str, dict]]) -> Tuple[List[Tuple[str, int]], List[str]]:
    indicators = []
    tickers = []
    
    def parse_condition(condition):
            if condition:
                lh_indicator = condition.get("lh_indicator", {})
                rh_indicator = condition.get("rh_indicator", {})
                lh_type = lh_indicator.get("type")
                rh_type = rh_indicator.get("type")
                lh_window = lh_indicator.get("window", 0)
                rh_window = rh_indicator.get("window", 0)
                if lh_type:
                    indicators.append((lh_type, lh_window))
                if rh_type:
                    indicators.append((rh_type, rh_window))
                lh_ticker = condition.get("lh_ticker_symbol")
                rh_ticker = condition.get("rh_ticker_symbol")
                if lh_ticker:
                    tickers.append(lh_ticker)
                if rh_ticker:
                    tickers.append(rh_ticker)

    def parse_recursively(incantation: Dict[str, Union[str, dict]]):
        if not incantation:
            return
        
        incantation_type = incantation.get("incantation_type")

        if incantation_type:
            if incantation_type == "IfElse":
                if "then_incantation" in incantation:
                    parse_recursively(incantation["then_incantation"])
                if "else_incantation" in incantation:
                    parse_recursively(incantation["else_incantation"])
                    
            if incantation_type == "Weighted":
                if incantation.get("type") == "InverseVolatility":
                    indicators.append(("Volatility", incantation.get("inverse_volatility_window")))
            
            if incantation_type == "Ticker":
                symbol = incantation.get("symbol")
                if symbol:
                    tickers.append(symbol)
            
            if incantation_type == "Filtered":
                sort_indicator = incantation.get("sort_indicator")
                indicators.append((sort_indicator.get("type"), sort_indicator.get("window")))
                if incantation.get("weight_type") == "InverseVolatility":
                    indicators.append(("Volatility", incantation.get("inverse_volatility_window")))
            
            if "incantations" in incantation: # applys to weighted/filtered/switch
                for sub_incantation in incantation["incantations"]:
                    parse_recursively(sub_incantation)
            
            if "condition" in incantation:
                parse_condition(incantation["condition"])
            
            if "conditions" in incantation:
                for condition in incantation["conditions"]:
                    parse_condition(condition)


    parse_recursively(strategy["incantation"])

    # Remove duplicates by converting to set, then back to list
    unique_indicators = list(set(indicators))
    unique_tickers = list(set(tickers))

    return unique_indicators, unique_tickers

# from typing import Dict, List, Tuple, Union
# def parse_strategy(data: Dict[str, Union[str, dict]]) -> Tuple[List[Tuple[str, int]], List[str]]:
#     # Initialize sets for indicators and symbols
#     indicators = set()
#     symbols = set()

#     def parse_condition(condition):
#         if "lh_indicator" in condition:
#             lh_indicator = condition["lh_indicator"]["type"]
#             lh_period = condition["lh_indicator"].get("window", None)
#             indicators.add((lh_indicator, lh_period))
#         if "rh_indicator" in condition:
#             rh_indicator = condition["rh_indicator"]["type"]
#             rh_period = condition["rh_indicator"].get("window", None)
#             indicators.add((rh_indicator, rh_period))
#         if "lh_ticker_symbol" in condition and condition["lh_ticker_symbol"]:
#             symbols.add(condition["lh_ticker_symbol"])
#         if "rh_ticker_symbol" in condition and condition["rh_ticker_symbol"]:
#             symbols.add(condition["rh_ticker_symbol"])

#     def parse_incantation(incantation):
#         if incantation:
#             if "condition" in incantation:
#                 parse_condition(incantation["condition"])
#             if "else_incantation" in incantation and incantation["else_incantation"]:
#                 parse_incantation(incantation["else_incantation"])
#             if "then_incantation" in incantation and incantation["then_incantation"]:
#                 if incantation["then_incantation"]["incantation_type"] == "Ticker":
#                     symbols.add(incantation["then_incantation"]["symbol"])
#                 else:
#                     parse_incantation(incantation["then_incantation"])

#     # Parse the top-level incantation
#     parse_incantation(data["incantation"])

#     # Convert sets to lists
#     indicator_list = list(indicators)
#     symbol_list = list(symbols)

#     return indicator_list, symbol_list