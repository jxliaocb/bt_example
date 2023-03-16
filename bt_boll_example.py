import backtrader as bt
import pandas as pd
import yfinance as yf

# Define parameters
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

symbol = 'A2M.AX'

# # Download data from Yahoo Finance
# data = bt.feeds.PandasData(dataname=yf.download(symbol, start=start_date, end=end_date))

# Data from local csv file from yahoo finance history
datapath = ('./yf/A2M.AX.csv')
dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
dataframe['openinterest'] = 0
data = bt.feeds.PandasData(dataname=dataframe)

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
