# 海龟交易法则概述
# 海龟交易法则是最容易实现的一个完整量化交易策略，本质是跟随模型，通过唐安奇通道突破方法确定入场离场信号。一个完整的海龟交易，需要确定的事情有：

# 市场：买卖什么；
# 头寸规模：买卖多少；
# 入市：什么时候买卖；
# 止损：什么时候放弃一个亏损的头寸；
# 退出：什么时候退出一个盈利的头寸；
# 战术：怎么买卖。
# 海龟交易法则所需指标
# 唐奇安通道
# 唐奇安上阻力线 - 由过去N天的当日最高价的最大值，Max(最高价，N)

# 唐奇安下支撑线 - 由过去M天的当日最低价的最小值形成，Min(最低价，M）

# 中心线 - （上线 + 下线）/ 2

# 真实波动AR
# 真实波幅： 是以下三个值中的最大值：

# (1) 当前交易日最高价和最低价的波幅；

# (2) 前一交易日的收盘价与当前交易日最高价的波幅；

# (3) 前一交易日的收盘价与当前交易日最低价的波幅。

# TrueRange（TR）=Max(High−Low,High−PreClose,PreClose−Low)

# 真实波动幅度均值ATR(N值）
# ATR=MA(TR,M)，即对真实波幅TR进行N日移动平均计算。

# 建仓单位：Unit=(1%∗账户总资金)/N
# 建仓单位的意义就是，让一个N值的波动与你总资金1%的波动对应，如果买入1unit单位的资产，当天震幅使得总资产的变化不超过1%。

# 海龟交易具体策略
# 入场：最新价格为20日价格高点，买入一单元股票
# 加仓：最新价格>上一次买入价格+0.5*ATR，买入一单元股票，最多3次加仓
# 出场：最新价格为10日价格低点，清空仓位
# 止损：最新价格<上一次买入价格-2*ATR，清空仓位
# backtrader回测代码
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import datetime
import backtrader as bt
import pandas as pd


class TestSizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return self.p.stake
        position = self.broker.getposition(data)
        if not position.size:
            return 0
        else:
            return position.size
        return self.p.stake


class TestStrategy(bt.Strategy):
    params = (('maperiod', 15),  ('printlog', False), )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.newstake = 0
        self.buytime = 0
        # 参数计算，唐奇安通道上轨、唐奇安通道下轨、ATR
        self.DonchianHi = bt.indicators.Highest(
            self.datahigh(-1), period=20, subplot=False)
        self.DonchianLo = bt.indicators.Lowest(
            self.datalow(-1), period=10, subplot=False)
        self.TR = bt.indicators.Max((self.datahigh(0) - self.datalow(0)), abs(
            self.dataclose(-1) - self.datahigh(0)), abs(self.dataclose(-1) - self.datalow(0)))
        self.ATR = bt.indicators.SimpleMovingAverage(
            self.TR, period=14, subplot=True)
        # 唐奇安通道上轨突破、唐奇安通道下轨突破
        self.CrossoverHi = bt.ind.CrossOver(self.dataclose(0), self.DonchianHi)
        self.CrossoverLo = bt.ind.CrossOver(self.dataclose(0), self.DonchianLo)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                (order.executed.price,
                order.executed.value,
                order.executed.comm), doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                     (order.executed.price,
                     order.executed.value,
                     order.executed.comm), doprint=True)
                self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return
        # 入场
        if self.CrossoverHi > 0 and self.buytime == 0:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.buytime = 1
            self.order = self.buy()
        # 加仓
        elif self.datas[0].close > self.buyprice+0.5*self.ATR[0] and self.buytime > 0 and self.buytime < 5:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.order = self.buy()
            self.buytime = self.buytime + 1
        # 出场
        elif self.CrossoverLo < 0 and self.buytime > 0:
            self.order = self.sell()
            self.buytime = 0
        # 止损
        elif self.datas[0].close < (self.buyprice - 2*self.ATR[0]) and self.buytime > 0:
            self.order = self.sell()
            self.buytime = 0
   
    def stop(self):        
        self.log('(MA Period %2d) Ending Value %.2f' % (self.params.maperiod, self.broker.getvalue()), doprint=True)


if __name__ == '__main__':    
    # 创建主控制器    
    cerebro = bt.Cerebro()    
    # 加入策略    
    cerebro.addstrategy(TestStrategy)   
    # 准备股票日线数据，输入到backtrader    
    datapath = ('./yf/A2M.AX.csv')   
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)                            
    dataframe['openinterest'] = 0    
    data = bt.feeds.PandasData(dataname=dataframe,fromdate=datetime.datetime(2008, 1, 8),  todate=datetime.datetime(2019, 12, 31))    
    cerebro.adddata(data)    
    # broker设置资金、手续费    
    cerebro.broker.setcash(100000.0)    
    cerebro.broker.setcommission(commission=0.003)
    # 设置买入策略    
    cerebro.addsizer(TestSizer)    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())   
    # 启动回测    
    cerebro.run()    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())    
    # 曲线绘图输出    
    # cerebro.plot()