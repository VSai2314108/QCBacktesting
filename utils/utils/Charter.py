from AlgorithmImports import *

class Charter():
    def __init__(self, alpha):
        self.algo = alpha.customAlgo
        self.alpha = alpha
        chart = Chart(alpha.name)
        self.algo.add_chart(chart)
        chart.add_series(Series("PV", SeriesType.LINE, "$", Color.White))
        chart.add_series(Series("PV w. Slope", SeriesType.LINE, "$", Color.GREEN))
        chart.add_series(Series("Long", SeriesType.SCATTER, "$", Color.Green))
        chart.add_series(Series("Short", SeriesType.SCATTER, "$", Color.Red))
        chart.add_series(Series("Neutral", SeriesType.SCATTER, "$", Color.Gray))
    
    def update(self):
        portfolioValue = self.alpha.sim_portfolio.equity
        realPortfolioValue = self.alpha.real_portfolio.equity
        self.algo.plot(self.alpha.name,"PV",portfolioValue)
        self.algo.plot(self.alpha.name,"PV w. Slope",realPortfolioValue)
        if self.alpha.lin_reg_slope.IsReady:
            signal = self.alpha.lin_reg_slope.Signal
            if signal == 1:
                self.algo.plot(self.alpha.name,"Long",portfolioValue)
            if signal == -1:
                self.algo.plot(self.alpha.name,"Short",portfolioValue)
            if signal == 0:
                self.algo.plot(self.alpha.name,"Neutral",portfolioValue)