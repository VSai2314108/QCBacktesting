from AlgorithmImports import *
from typing import List, Tuple, Dict, Union, Optional
from enum import Enum

class IncantationType(Enum):
    SWITCH = 1
    WEIGHTED = 2
    TICKER = 3
    FILTERED = 4
    IFELSE = 5

def parse_strategy(strategy: Dict[str, Union[str, dict]]) -> Tuple[List[Tuple[str, int]], List[str]]:
    """
    Parses a strategy dictionary and extracts the indicators and tickers used in the strategy.

    Args:
        strategy (Dict[str, Union[str, dict]]): The strategy dictionary to parse.

    Returns:
        Tuple[List[Tuple[str, int]], List[str]]: A tuple containing the unique indicators and tickers extracted from the strategy.

    """
    indicators = []
    tickers = []
    
    def parse_condition(condition):
        # Function to parse a condition dictionary and extract indicators and tickers
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
        # Recursive function to parse the incantation dictionary and extract indicators and tickers
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
            
            if "incantations" in incantation: # applies to weighted/filtered/switch
                for sub_incantation in incantation["incantations"]:
                    parse_recursively(sub_incantation)
            
            if "condition" in incantation:
                parse_condition(incantation["condition"])
            
            if "conditions" in incantation:
                for condition in incantation["conditions"]:
                    parse_condition(condition)


    parse_recursively(strategy["incantation"])

    # Remove duplicates by converting to set, then back to list
    unique_indicators = set(indicators)
    unique_tickers = set(tickers)

    return unique_indicators, unique_tickers
    
def evaluate_strategy(algo, incantation: Optional[Dict[str, dict]] = None, cur_weight: float = 1) -> List[Tuple[str, float]]:
    if not incantation:
        return []        
    incantation_type = incantation.get("incantation_type")
    incantation_enum = IncantationType[incantation_type.upper()]

    if incantation_enum == IncantationType.SWITCH:
        return switch_strategy(algo, incantation, cur_weight)
    elif incantation_enum == IncantationType.WEIGHTED:
        return weighted_strategy(algo, incantation, cur_weight)
    elif incantation_enum == IncantationType.TICKER:
        return ticker_strategy(algo, incantation, cur_weight)
    elif incantation_enum == IncantationType.FILTERED:
        return filtered_strategy(algo, incantation, cur_weight)
    elif incantation_enum == IncantationType.IFELSE:
        return if_else_strategy(algo, incantation, cur_weight)
    return []

def switch_strategy(algo, incantation: Dict[str, dict], cur_weight: float) -> List[Tuple[str, float]]:
    conditions = incantation.get("conditions")
    cond_results = [evaluate_condition(algo, condition) for condition in conditions]
    incantation_index = len(conditions) - sum(cond_results)
    result_incantation = incantation.get("incantations")[incantation_index]
    return evaluate_strategy(algo, result_incantation, cur_weight)

def weighted_strategy(algo, incantation: Dict[str, dict], cur_weight: float) -> List[Tuple[str, float]]:
    weight_type = incantation.get("type")
    incantations = incantation.get("incantations")
    if weight_type == "Equal":
        # redsitribute the weight equally among the active incantations ( NOT [])
        outputs = [evaluate_strategy(algo, incantation, cur_weight) for incantation in incantations]
        
        # divide weight by the number of non-empty outputs
        active_branches = len([output for output in outputs if output!=[]])
        outputs = [(item[0], item[1]*(1/active_branches)) for sublist in outputs for item in sublist]
        return outputs
    elif weight_type == "Custom":
        weights = incantation.get("weights")
        outputs = []
        for i, incantation in enumerate(incantations):
            outputs.append(evaluate_strategy(algo, incantation, cur_weight * (weights[i]/100.0)))
        outputs = [item for sublist in outputs for item in sublist]
        return outputs
    elif weight_type == "InverseVolatility": # implement this eventually
        volatility_window = incantation.get("inverse_volatility_window")
        outputs = [evaluate_strategy(algo, incantation, cur_weight) for incantation in incantations]
        
        # calculate inverse volatility for each sublist
        inverse_volatilities = []
        for output in outputs:
            temp_inverse_vol_sum = 0
            for ticker, weight in output: # not sure if weight is used here
                volatility_key = f"Volatility_{ticker}_{volatility_window}"
                temp_inverse_vol_sum += 1/algo.indicators.get(volatility_key).value
            inverse_volatilities.append(temp_inverse_vol_sum)
        
        # calculate weights
        total_inverse_volatility = sum(inverse_volatilities)
        for output, inverse_volatility in zip(outputs, inverse_volatilities):
            for i in range(len(output)):
                output[i] = (output[i][0], output[i][1] * (inverse_volatility / total_inverse_volatility))
        
        return outputs
            
def ticker_strategy(algo, incantation: Dict[str, dict], cur_weight: float) -> List[Tuple[str, float]]:
    return [(incantation.get("symbol"), cur_weight)]

def filtered_strategy(algo, incantation: Dict[str, dict], cur_weight: float) -> List[Tuple[str, float]]:
    sort_indicator = incantation.get("sort_indicator").get("type")
    sort_indicator_window = incantation.get("sort_indicator").get("window")
    mx = not incantation.get("bottom")
    count = incantation.get("count")
    incantations = incantation.get("incantations")
    
    outputs = [evaluate_strategy(algo, incantation, cur_weight) for incantation in incantations]
    
    # evaluate the sort indicator for all tickers in each sublist and computer weighted average, then sort
    outputs_with_indicator = [] #([(ticker,weight), ...], indicator_value)
    for output in outputs:
        temp_val = 0
        temp_weights = 0
        for ticker, weight in output:
            sort_indicator_key = f"{sort_indicator}_{ticker}_{sort_indicator_window}"
            sort_indicator_value = algo.indicators.get(sort_indicator_key).value
            temp_val += sort_indicator_value
            temp_weights += weight
        outputs_with_indicator.append((output, (temp_val / temp_weights)))
    
    outputs_with_indicator.sort(key=lambda x: x[1], reverse=mx)
    outputs_with_indicator = outputs_with_indicator[:count]
    
    outputs = [output for output, _ in outputs_with_indicator]
    
    # apply the weighting methods to the outputs
    weight_type = incantation.get("weight_type")
    inverse_volatility_window = incantation.get("inverse_volatility_window")
    weights = incantation.get("weights")
    if weight_type == "Equal":
        outputs = [(item[0], item[1]*(1/count)) for sublist in outputs for item in sublist]
        return outputs
    elif weight_type == "Custom":
        for sublist in outputs:
            for i in range(len(sublist)):
                sublist[i] = (sublist[i][0], sublist[i][1] * (weights[i]/100.0))
        outputs = [item for sublist in outputs for item in sublist]
        return outputs
    elif weight_type == "InverseVolatility":
        inverse_volatilities = []
        for output in outputs:
            temp_inverse_vol_sum = 0
            for ticker, weight in output:
                volatility_key = f"Volatility_{ticker}_{inverse_volatility_window}"
                temp_inverse_vol_sum += 1/algo.indicators.get(volatility_key).value
            inverse_volatilities.append(temp_inverse_vol_sum)
        
        # calculate weights
        total_inverse_volatility = sum(inverse_volatilities)
        for output, inverse_volatility in zip(outputs, inverse_volatilities):
            for i in range(len(output)):
                output[i] = (output[i][0], output[i][1] * (inverse_volatility / total_inverse_volatility))
        
        outputs = [item for sublist in outputs for item in sublist]
        return outputs
    
def if_else_strategy(algo, incantation: Dict[str, dict], cur_weight: float) -> List[Tuple[str, float]]:
    condition = incantation.get("condition")
    if evaluate_condition(algo, condition):
        then_incantation = incantation.get("then_incantation")
        return evaluate_strategy(algo, then_incantation, cur_weight=cur_weight)
    else:
        else_incantation = incantation.get("else_incantation")
        return evaluate_strategy(algo, else_incantation, cur_weight=cur_weight)

def evaluate_condition(algo, condition: Optional[Dict[str, dict]]):
    condition_type = condition.get("condition_type")
    if condition_type == "AllOf":
        return all([evaluate_condition(algo, c) for c in condition.get("conditions")])
    elif condition_type == "AnyOf":
        return any([evaluate_condition(algo, c) for c in condition.get("conditions")])
    elif condition_type == "SingleCondition":
        lh_value, rh_value = 0, 0
        if condition["type"] == "Month":
            lh_ticker = condition["lh_ticker_symbol"]
            lh_value = algo.indicators.get("Month_0").value
            rh_value = condition["rh_value"]
        else:
            lh_indicator = condition["lh_indicator"]["type"]
            lh_period = condition["lh_indicator"].get("window", None)
            lh_ticker = condition["lh_ticker_symbol"]
            lh_value = algo.indicators.get(f"{lh_indicator}_{lh_ticker}_{lh_period}").value
            if condition["type"] == "BothIndicators":
                rh_indicator = condition["rh_indicator"]["type"]
                rh_period = condition["rh_indicator"].get("window", None)
                rh_ticker = condition["rh_ticker_symbol"]
                rh_value = algo.indicators.get(f"{rh_indicator}_{rh_ticker}_{rh_period}").value
            elif condition["type"] == "IndicatorAndNumber":
                rh_value = condition["rh_value"]
            else:
                raise ValueError("Invalid condition type")
                
        # evaluate
        if condition.get("greater_than"):
            return lh_value > (rh_value + condition.get("rh_bias", 0))
        else:
            return lh_value <= (rh_value + condition.get("rh_bias", 0))