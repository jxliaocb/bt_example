from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime  
import os.path  
import sys  
import backtrader as bt
import tushare as ts
import argparse
import pandas as pd

class TestStrategy(bt.Strategy):    
    params = (        
        ('maperiod', 15),
        ('printlog', False),
    )    

    def log(self, txt, dt=None, doprint=False): 
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)      

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:                          
            return       
        if order.status in [order.Completed]:           
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f '%
                        (order.executed.price,
                        order.executed.value,
                        order.executed.comm))                

                self.buyprice = order.executed.price                
                self.buycomm = order.executed.comm
            else:              
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %                         
                        (order.executed.price,                          
                        order.executed.value,                          
                        order.executed.comm)) 

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
        self.log('Close, %.2f' % self.dataclose[0])       
        if self.order:           
            return        
        # 简单策略，当日收盘价大于简单滑动平均值买入，当日收盘价小于简单滑动平均值卖出
        if not self.position:           
            if self.dataclose[0] > self.sma[0]:            
                self.log('BUY CREATE, %.2f' % self.dataclose[0])             
                self.order = self.buy()       
        else:
            if self.dataclose[0] < self.sma[0]:              
                self.log('SELL CREATE, %.2f' % self.dataclose[0])              
                self.order = self.sell()   
    def stop(self):       
        self.log('(MA Period %2d) Ending Value %.2f' %
        (self.params.maperiod, self.broker.getvalue()), doprint=True)

if __name__ == '__main__':    
    #创建主控制器
    cerebro = bt.Cerebro()      
    #导入策略参数寻优
    cerebro.addstrategy(TestStrategy)    
    #准备股票日线数据，输入到backtrader
    start='2021-10-8'
    end='2022-12-31'
    df = ts.get_k_data('600837', start=start, end=end)
    df.to_csv  ('./tushare/600837.csv')
    datapath = ('./tushare/600837.csv')                      
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)    
    dataframe['openinterest'] = 0   
    data = bt.feeds.PandasData(dataname=dataframe,                               
                        fromdate=start,                               
                        todate=end                               
    )    
    cerebro.adddata(data)
    #broker设置资金、手续费
    cerebro.broker.setcash(1000.0)           
    cerebro.broker.setcommission(commission=0.001)    
    #设置买入设置，策略，数量
    # cerebro.addsizer(bt.sizers.FixedSize, stake=10)   
    # print('Starting Portfolio Value: %.2f' %cerebro.broker.getvalue())    
    cerebro.run()    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue()) 