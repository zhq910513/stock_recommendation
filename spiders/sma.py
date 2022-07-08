import copy
import datetime
import json
import re
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from lxml import etree
from matplotlib.pylab import date2num
from mplfinance.original_flavor import candlestick_ohlc


def default_data():
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
        date = str(pd.to_datetime(copy.deepcopy(l[0]))).split(' ')[0]
        l[0] = date
        data.append(l)
    return data[::]


def df_data(data_list):
    arr = np.array(data_list)
    df = pd.DataFrame(arr)  # 将数据转为DataFrame数据类型

    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'Market Cap']  # 设置列标题
    df = df.astype({'open': 'float64', 'high': 'float64', 'low': 'float64', 'close': 'float64', 'volume': 'float64','Market Cap': 'float64'})

    plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴刻度负号乱码
    plt.rcParams['font.sans-serif'] = ['Simhei']  # 解决中文乱码问题

    df['date'] = df['date'].apply(lambda x: date2num(datetime.datetime.strptime(x, '%Y-%m-%d')))  # 转换日期格式
    return df


def draw_price(df):
    fig, ax1 = plt.subplots(figsize=(1200 / 72, 480 / 72))
    da = df[['date', 'open', 'high', 'low', 'close']]
    f = da[['date', 'open', 'high', 'low', 'close']].values
    ax3 = ax1.twinx()
    ax2 = ax1.twinx()
    candlestick_ohlc(ax1, f, colordown='g', colorup='r', width=0.3, alpha=0.7)
    ax3.bar(df['date'], df['volume'], width=0.6)
    ax2.plot(df['date'], df['close'])
    ax2.grid(True)
    ax3.grid(True)
    ax3.set_ylim(0, 100000)
    ax1.set_ylim(0, 50)
    ax2.set_ylim(0, 50)
    ax1.set_ylabel('$')
    fig.subplots_adjust(bottom=0.2)  ## 调整底部距离
    ax1.xaxis_date()  ## 设置X轴刻度为日期时间
    ax2.xaxis_date()  ## 设置X轴刻度为日期时间
    ax3.xaxis_date()  ## 设置X轴刻度为日期时间
    plt.yticks()  ## 设置Y轴刻度线
    plt.xlabel(u"时间")  ##设置X轴标题
    ax2.set_ylabel('收盘价/成交量')
    plt.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)  ##设置网格线
    plt.show()


def draw_sma(df):
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


def req_history_data(stock_code):
    url = f'http://78.push2his.eastmoney.com/api/qt/stock/kline/get' \
          f'?cb=jQuery' \
          f'&secid=0.{stock_code}' \
          f'&ut=fa5fd1943c7b386f172d6893dbfba10b' \
          f'&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6' \
          f'&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61' \
          f'&klt=101' \
          f'&fqt=0' \
          f'&end=20500101' \
          f'&lmt=120' \
          f'&_={int(time.time() * 1000)}'

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'qgqp_b_id=e829d607b6454c6dde64109c61f936e2; st_si=21280292358923; HAList=a-sz-000756-%u65B0%u534E%u5236%u836F; em_hq_fls=js; st_pvi=94651109933561; st_sp=2022-06-11%2016%3A19%3A10; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=17; st_psi=20220611165158402-113200301201-7930304906; st_asi=delete',
        'Host': '46.push2his.eastmoney.com',
        'Referer': 'http://quote.eastmoney.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    resp = requests.get(url=url, headers=headers)
    resp_data = json.loads(re.findall('\((.*?)\)', resp.text, re.S)[0]).get('data')
    his_list = resp_data.get('klines')

    data_list = []
    for data in his_list:
        data = data.split(',')
        new_data = [data[0]]
        for i in data[1:7]:
            new_data.append(round(float(i), 2))
        data_list.append(new_data)
    return data_list


if __name__ == '__main__':
    # d_l = default_data()
    # df = df_data(d_l)
    # print(df)

    d_ll = req_history_data('000722')
    df = df_data(d_ll)
    print(df)

    # draw_price(df)
