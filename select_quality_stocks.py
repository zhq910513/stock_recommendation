#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: stock_recommendation
@file: stock_format_data.py
@time: 2022/6/11 16:30
"""

import json
import pprint
from multiprocessing.pool import ThreadPool

import requests
from bs4 import BeautifulSoup
from pylab import *

from pipelines import MongoPipeline

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体（解决中文无法显示的问题）
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号“-”显示方块的问题

pp = pprint.PrettyPrinter(indent=4)

names = [
    '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'
]

# 标准数据
format_data = [-2.86, -0.56, -3.09, 0.49, -1.9, -1.0, 0.21, 0.26, 0.22, 0.31, -2.42, -0.29, -1.15, 0.47, 0.52, 1.44, 1.96, -0.43, 2.26, 0.67, -1.2, 2.23, 0.02, 0.61, 0.65, 1.63, 1.48, 0.41, 3.73, 5.73]

# 是否显示画图
show = False

# 保存数据
save_data = {'update_time': time.strftime("%Y-%m-%d", time.localtime(time.time()))}


# 获取本期龙虎榜
def select_stocks():
    # return [
    #     '002988',
    #     '000025',
    #     '002339',
    #     '002380',
    #     '002272',
    #     '002986',
    #     '002945',
    #     '000722',
    #     '000756',
    #     '002101'
    # ]
    return req_longhu_stocks()


# 龙虎榜数据
def req_longhu_stocks():
    url = 'http://data.10jqka.com.cn/rank/lxsz/field/lxts/order/asc/page/1/ajax/1/free/1/'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'v=AwQz8x0GOl_PKY6Tm8qKixUm1YnzHSiH6kG8yx6lkE-SSaq3Ri34FzpRjFpt',
        'Host': 'data.10jqka.com.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://data.10jqka.com.cn/rank/lxsz/field/lxts/order/asc/page/1/ajax/1/free/1/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
    }
    resp = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        stocks = []
        for tr in soup.find_all('tr'):
            try:
                stock_code = tr.find_all('td')[1].get_text()
                up_days = tr.find_all('td')[6].get_text()
                if int(up_days) <= 3 and str(stock_code).startswith('00') and '退' not in str(tr):
                    stocks.append(stock_code)
            except:
                pass
        return stocks
    except Exception as error:
        print(error)


# 东方财富历史数据
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
    stock_name = resp_data.get('name')
    his_rate = []
    for h in resp_data.get('klines')[-43:-13]:
        detail_data = h.split(',')
        his_rate.append(float(detail_data[8]))
    last_price = resp_data.get('klines')[-1].split(',')
    last_detail = dict(zip(names, last_price))
    return stock_code, stock_name, his_rate, last_detail


# 对齐标准数据
def alignment_data(n, m):
    start = n[0]
    dis = start - m[0]
    new_list = []
    for x in m:
        new_list.append(round(float(x + dis), 2))
    return dis, new_list


# 获取最近30天交易数据
def get_30_days_data(stock_code):
    stock_code, stock_name, stock_history_data, last_detail = req_history_data(stock_code)
    dis, stock_history_data = alignment_data(format_data, stock_history_data)
    return {'stock_code': stock_code, 'stock_name': stock_name, 'stock_history_data': stock_history_data, 'dis': dis,
            'last_detail': last_detail}


# 相似度计算
def handle_dtw(a, b):
    x = len(a)
    y = len(b)
    dist = [[0 for i in range(x)] for j in range(y)]
    G = [[0 for i in range(x)] for j in range(y)]
    for j in range(y):
        for i in range(x):
            dist[j][i] = abs(a[i] - b[j])
    G[0][0] = dist[0][0] * 2
    for j in range(y - 1):
        G[j + 1][0] = G[j][0] + dist[j + 1][0]
    for i in range(x - 1):
        G[0][i + 1] = G[0][i] + dist[0][i + 1]
    for j in range(y - 1):
        for i in range(x - 1):
            G[j + 1][i + 1] = min((G[j][i + 1] + dist[j + 1][i + 1]), (G[j + 1][i] + dist[j + 1][i + 1]),
                                  (G[j][i] + 2 * dist[j + 1][i + 1]))
    return G[y - 1][x - 1]


# 多线程处理数据
def thread_search(remove_bad=False, Async=True):
    thread_list = []

    # 设置进程数
    pool = ThreadPool(processes=4)

    stock_code_list = select_stocks()
    save_data.update({'stock_code_list': stock_code_list})
    for info in stock_code_list:
        if Async:
            out = pool.apply_async(func=get_30_days_data, args=(info,))  # 异步
        else:
            out = pool.apply(func=get_30_days_data, args=(info,))  # 同步
        thread_list.append(out)

    pool.close()
    pool.join()

    # 获取输出结果
    com_list = []
    if Async:
        for p in thread_list:
            com = p.get()  # get会阻塞
            com_list.append(com)
    else:
        com_list = thread_list
    if remove_bad:
        com_list = [i for i in com_list if i is not None]
    return com_list


# 获取曲线相似度结果
def get_result(stock_list=None):
    if not stock_list:
        print('--- 获取龙虎榜失败 ---')
        return
    names = []
    results = []
    for stock_data in stock_list:
        stock_name = stock_data['stock_name']
        stock_history_data = stock_data['stock_history_data']
        stock_result = handle_dtw(format_data, stock_history_data)
        names.append(stock_name)
        results.append(stock_result)
    best_stock_name = names[results.index(min(results))]
    for stock_data in stock_list:
        if stock_data.get('stock_name') == best_stock_name:
            last_detail = stock_data['last_detail']
            save_data.update({'best_stock_code': stock_data["stock_code"], 'best_stock_name': best_stock_name, 'last_detail': last_detail})
            print(f'本期最接近标准线的是：{stock_data["stock_code"]} {best_stock_name}\n最后收盘信息：{last_detail}')

    # 画图
    if show:
        draw(stock_list)

    # save
    MongoPipeline('daily_info').update_item({'update_time': None, 'best_stock_code': None}, save_data)


# 画图
def draw(stock_list):
    x = np.linspace(0, 1, 30)
    plt.figure()

    # 画标准数据线
    plt.plot(x, format_data, label='标准')

    # 画其他数据线
    for stock_data in stock_list:
        plt.plot(x, stock_data['stock_history_data'], linestyle='--', label=stock_data['stock_name'])

    plt.legend(loc=0)
    plt.show()


if __name__ == '__main__':
    stock_history = thread_search()
    get_result(stock_history)
