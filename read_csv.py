import datetime
import backtrader as bt
import backtrader.feeds as btfeed


data = btfeed.GenericCSVData(
    dataname='./datas_yf/A2M.AX.csv',

)
print(data.lines)