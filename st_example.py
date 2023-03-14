import backtrader as bt
from datetime import datetime


class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=20)

    def next(self):
        if self.data.close > self.sma:
            self.buy()
        elif self.data.close < self.sma:
            self.sell()

cerebro = bt.Cerebro()
cerebro.broker.set_cash(100000)
data = bt.feeds.YahooFinanceData(dataname='AAPL.csv', fromdate=datetime(
    2022, 3, 4), todate=datetime(2023, 3, 4))
cerebro.adddata(data)
cerebro.addstrategy(MyStrategy)
cerebro.run()
cerebro.plot()
