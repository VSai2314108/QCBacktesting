from hmac import new
from AlgorithmImports import *
from datetime import timedelta, datetime

class SimulatedPortfolio():
    def __init__(self, alpha, starting_value, lin_slope=False) -> None:
        self.equity = starting_value
        self.cash = starting_value
        self.alpha = alpha
        self.algo: QCAlgorithm = alpha.customAlgo
        self.allocations = {symbol: (0,0,0) for symbol in self.alpha.symbols} # allocation, shares, last price
        self.pvalues = []
        self.lin_slope = lin_slope
    
    def _update(self):
        current_prices = {symbol: self.algo.securities[symbol].close for symbol in self.alpha.symbols}
        changes = {symbol: algo_allocation - self.allocations[symbol][0] for symbol, algo_allocation in self.alpha.allocations.items()}
        ordering = sorted(changes.items(), key=lambda x: x[1])
        
        # iterate over the changes recomputing equity at each step
        for symbol, change in ordering:
            new_allocation = self.allocations[symbol][0]+change # portfolio allocation after update
            if self.lin_slope and self.alpha.lin_reg_slope.Signal not in [1,None]:
                new_allocation = 0
                self.cash += self.allocations[symbol][1] * current_prices[symbol]
                self.allocations[symbol] = (new_allocation, 0, current_prices[symbol])
            elif change == 0:
                self.allocations[symbol] = (self.allocations[symbol][0], self.allocations[symbol][1], current_prices[symbol])
            elif change > 0:
                shares = self.allocations[symbol][1]
                new_shares = (change * self.equity) // current_prices[symbol] # compute shares we are buying
                self.cash += -(new_shares * current_prices[symbol])
                self.allocations[symbol] = (new_allocation, shares+new_shares, current_prices[symbol])
            else:
                # sell
                shares = self.allocations[symbol][1]
                new_shares = int(shares * change) # compute the sahres we are buying (should be negative)
                self.cash += -(new_shares * current_prices[symbol])
                self.allocations[symbol] = (new_allocation, shares+new_shares, current_prices[symbol])
            self.equity = sum([allocation[1] * allocation[2] for allocation in self.allocations.values()]) + self.cash
            self.pvalues.append(self.equity)
        self.algo.log(f"{self.alpha.name} Equity: {self.equity}")