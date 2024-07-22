from typing import Dict, List, Tuple, Union
def parse_strategy(data: Dict[str, Union[str, dict]]) -> Tuple[List[Tuple[str, int]], List[str]]:
    # Initialize sets for indicators and symbols
    indicators = set()
    symbols = set()

    def parse_condition(condition):
        if "lh_indicator" in condition:
            lh_indicator = condition["lh_indicator"]["type"]
            lh_period = condition["lh_indicator"].get("window", None)
            indicators.add((lh_indicator, lh_period))
        if "rh_indicator" in condition:
            rh_indicator = condition["rh_indicator"]["type"]
            rh_period = condition["rh_indicator"].get("window", None)
            indicators.add((rh_indicator, rh_period))
        if "lh_ticker_symbol" in condition and condition["lh_ticker_symbol"]:
            symbols.add(condition["lh_ticker_symbol"])
        if "rh_ticker_symbol" in condition and condition["rh_ticker_symbol"]:
            symbols.add(condition["rh_ticker_symbol"])

    def parse_incantation(incantation):
        if incantation:
            if "condition" in incantation:
                parse_condition(incantation["condition"])
            if "else_incantation" in incantation and incantation["else_incantation"]:
                parse_incantation(incantation["else_incantation"])
            if "then_incantation" in incantation and incantation["then_incantation"]:
                if incantation["then_incantation"]["incantation_type"] == "Ticker":
                    symbols.add(incantation["then_incantation"]["symbol"])
                else:
                    parse_incantation(incantation["then_incantation"])

    # Parse the top-level incantation
    parse_incantation(data["incantation"])

    # Convert sets to lists
    indicator_list = list(indicators)
    symbol_list = list(symbols)

    return indicator_list, symbol_list