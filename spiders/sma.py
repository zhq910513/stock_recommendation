import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lxml import etree
from matplotlib.pylab import date2num
from mplfinance.original_flavor import candlestick_ohlc

with open("../data.txt", "r") as f: rd = f.read()
selector = etree.HTML(rd)
url_infos = selector.xpath('//tr')
# 从data.txt中提取需要的数据
data = []
for url_info in url_infos:
    l = []
    # 获取单行数据并做初步处理
    for i in range(7):
        d = url_info.xpath('td[%d+1]/text()' % i)
        if i == 0:
            l += d
        else:
            if d[0] == '-':
                d[0] = np.nan
                l += d
            else:
                d[0] = d[0].replace(',', '')
                d[0] = d[0].strip('$')
                d[0] = float(d[0])
                l += d
    data.append(l)

arr = np.array(data)
df = pd.DataFrame(arr)  # 将数据转为DataFrame数据类型

df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'Market Cap']  # 设置列标题
# df['date']=df['date'].map(pd.to_datetime)#转化日期格式

df = df.astype({'open': 'float64', 'high': 'float64', 'low': 'float64', 'close': 'float64', 'volume': 'float64',
                'Market Cap': 'float64'})
df = df.reindex(index=df.index[::-1])
df.head()  # 倒序
df.reset_index(drop=True, inplace=True)  # 逆序后 重设index

plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴刻度负号乱码
plt.rcParams['font.sans-serif'] = ['Simhei']  # 解决中文乱码问题

df.reset_index(inplace=True)  # 重设index,原来的index汇入DataFrame中
df['date'] = pd.to_datetime(df['date'])
df = df.astype({'date': 'string'})
df.index = pd.to_datetime(df['date'])  # 设置index的值
print(df)
print(df.dtypes)
df['date'] = df['date'].apply(lambda x: date2num(datetime.datetime.strptime(x, '%Y-%m-%d')))  # 转换日期格式
print(df.dtypes)
print(df)

step = 5
dflen = len(df)
sma = {}
for i in range(step):
    sma[i] = 0
for i in range(dflen - step):
    i += step
    sma[i] = 0
    for j in range(step):
        j += 1
        sma[i] += df['close'][i - j]
        if j == step:
            sma[i] /= step
sma = pd.DataFrame.from_dict(sma, orient='index', columns=['5SMA'])
print(sma)

step = 30
dflen = len(df)
sma30 = {}
for i in range(step):
    sma30[i] = 0
for i in range(dflen - step):
    i += step
    sma30[i] = 0
    for j in range(step):
        j += 1
        sma30[i] += df['close'][i - j]
        if j == step:
            sma30[i] /= step
sma30 = pd.DataFrame.from_dict(sma30, orient='index', columns=['30SMA'])
print(sma30)

step = 60
dflen = len(df)
sma60 = {}
for i in range(step):
    sma60[i] = 0
for i in range(dflen - step):
    i += step
    sma60[i] = 0
    for j in range(step):
        j += 1
        sma60[i] += df['close'][i - j]
        if j == step:
            sma60[i] /= step
sma60 = pd.DataFrame.from_dict(sma60, orient='index', columns=['60SMA'])
print(sma60)

fig, ax1 = plt.subplots(figsize=(1200 / 72, 480 / 72))
da = df[['date', 'open', 'high', 'low', 'close']]
f = da[['date', 'open', 'high', 'low', 'close']].values
ax3 = ax1.twinx()
ax2 = ax1.twinx()
axsma = ax1.twinx()
axsma30 = ax1.twinx()
axsma60 = ax1.twinx()
candlestick_ohlc(ax1, f, colordown='g', colorup='r', width=0.3, alpha=0.7)
ax3.bar(df['date'], df['volume'], width=0.6)
ax2.plot(df['date'], df['close'])
axsma.plot(df['date'], sma['5SMA'], color="red")
axsma30.plot(df['date'], sma30['30SMA'], color="blue")
axsma60.plot(df['date'], sma60['60SMA'], color="green")
ax2.grid(True)
ax3.grid(True)
axsma.grid(True)
axsma30.grid(True)
axsma60.grid(True)
ax3.set_ylim(0, 500000000000)
ax1.set_ylim(0, 70000)
ax2.set_ylim(0, 70000)
axsma.set_ylim(0, 70000)
axsma30.set_ylim(0, 70000)
axsma60.set_ylim(0, 70000)
ax1.set_ylabel('币价$')
fig.subplots_adjust(bottom=0.2)  ## 调整底部距离
ax1.xaxis_date()  ## 设置X轴刻度为日期时间
ax2.xaxis_date()  ## 设置X轴刻度为日期时间
ax3.xaxis_date()  ## 设置X轴刻度为日期时间
axsma.xaxis_date()  ## 设置X轴刻度为日期时间
plt.yticks()  ## 设置Y轴刻度线
plt.xlabel(u"时间")  ##设置X轴标题
ax2.set_ylabel('收盘价/成交量/SMA')
plt.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)  ##设置网格线
plt.show()
