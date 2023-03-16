import backtrader as bt
import pandas as pd
import yfinance as yf
import datetime

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

# Download data from Yahoo Finance
# symbol = 'AAPL'
# start_date = '2015-01-01'
# end_date = '2023-03-04'
# data = bt.feeds.PandasData(dataname=yf.download(symbol, start=start_date, end=end_date))
datapath = ('./ak/600837.csv')
dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
dataframe.drop('日期.1', axis=1, inplace=True)
dataframe.rename(columns={'日期':'Date', '开盘':'Open', '收盘':'Close', '最高':'High', '最低':'Low', '成交量':'Volume' }, inplace = True)
dataframe['openinterest'] = 0
dataframe.to_csv('./yf/600837.csv')
data = bt.feeds.PandasData(dataname=dataframe)



# Create cerebro instance
cerebro = bt.Cerebro()

# Add data feed
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(BBStrategy)

# Add analyzer
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

# Run backtest
results = cerebro.run()

# Print results
# print(f"Cumulative Returns: {results[0].analyzers.returns.get_analysis()['cumulative']}")

# Plot results
# cerebro.plot()
