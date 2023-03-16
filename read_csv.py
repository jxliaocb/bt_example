import datetime
import backtrader as bt
import backtrader.feeds as btfeed
import yfinance as yf


# Download data from Yahoo Finance
# symbol = 'AAPL'
# start_date = '2015-01-01'
# end_date = '2023-03-04'
# dataname = yf.download(symbol, start=start_date, end=end_date)
# data = bt.feeds.PandasData(dataname)
# data.to_csv('./yf/AAPL.csv')

data = btfeed.GenericCSVData(
    dataname='./yf/A2M.AX.csv',

)
print(data)