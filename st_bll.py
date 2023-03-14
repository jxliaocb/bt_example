import backtrader as bt
import pandas as pd
import yfinance as yf

# Define parameters
symbol = 'AAPL'
start_date = '2015-01-01'
end_date = '2021-09-30'
window = 20
std = 2

class BBStrategy(bt.Strategy):
    params = (
        ('window', window),
        ('std', std)
    )
    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(period=self.params.window, devfactor=self.params.std)

    def next(self):
        if self.data.close < self.bollinger.lines.bot:
            self.buy()
        elif self.data.close > self.bollinger.lines.top:
            self.sell()

# Download data from Yahoo Finance
dataname=yf.download(symbol, start=start_date, end=end_date)
data = bt.feeds.PandasData(dataname)

# Create cerebro instance
cerebro = bt.Cerebro()

cerebro.broker.set_cash(100000)

# Add data feed
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(BBStrategy)

# Add analyzer
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

# Run backtest
results = cerebro.run()

print(cerebro.broker.get_cash())

# Print results
# print(f"Cumulative Returns: {results[0].analyzers.returns.get_analysis()['cumulative']}")

# Plot results
cerebro.plot()
