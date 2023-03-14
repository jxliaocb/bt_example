# https://github.com/teddykoker/blog

import pandas as pd
import datetime
import backtrader as bt
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

plt.rcParams["figure.figsize"] = (10, 6) # (w, h)

def sim_leverage(proxy, leverage=1, expense_ratio = 0.0, initial_value=1.0):
    """
    Simulates a leverage ETF given its proxy, leverage, and expense ratio.
    
    Daily percent change is calculated by taking the daily percent change of
    the proxy, subtracting the daily expense ratio, then multiplying by the leverage.
    """
    pct_change = proxy.pct_change(1)
    pct_change = (pct_change - expense_ratio / 252) * leverage
    sim = (1 + pct_change).cumprod() * initial_value
    sim[0] = initial_value
    return sim

start = datetime.datetime(1986, 5, 19)
end = datetime.datetime(2019, 1, 1)

data1 = bt.feeds.PandasData(dataname=yf.download(['VFINX'], start=start, end=end))

data2 = bt.feeds.PandasData(dataname=yf.download(['VUSTX'], start=start, end=end))
 

class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.getposition(self.data).size:
            self.order_target_percent(self.data, target=1.0)


def backtest(datas, strategy, plot=False, **kwargs):
    cerebro = bt.Cerebro()
    for data in datas:
        cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(strategy, **kwargs)
    results = cerebro.run()
    if plot:
        cerebro.plot()
    return (results[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
            results[0].analyzers.returns.get_analysis()['rnorm100'],
            results[0].analyzers.sharperatio.get_analysis()['sharperatio'])

dd, cagr, sharpe = backtest([data1, data2], BuyAndHold, plot=True)
print(f"Max Drawdown: {dd:.2f}%\nCAGR: {cagr:.2f}%\nSharpe: {sharpe:.3f}")