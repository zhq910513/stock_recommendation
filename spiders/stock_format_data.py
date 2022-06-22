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
import re
import time

import requests
from numpy import *

pp = pprint.PrettyPrinter(indent=4)

format_list = []

# 标准数据类型   high   low   aver   rate
def get_format_data(_type):
    if _type == 'high':
        _type_index = 3
        format_data = [13.99, 14.0, 13.57, 13.41, 13.38, 13.28, 13.31, 13.02, 12.53, 12.2, 11.18, 10.84, 10.85, 11.13,
                       11.4, 11.29, 11.41, 11.52, 11.85, 11.58, 12.64, 13.18, 12.6, 12.5, 12.28, 12.36, 12.56, 12.99,
                       13.46, 14.81]
    elif _type == 'low':
        _type_index = 4
        format_data = [13.43, 13.36, 13.37, 13.03, 12.91, 13.06, 12.85, 12.32, 12.01, 11.0, 10.47, 10.06, 10.41, 10.62,
                       10.88, 10.98, 11.18, 11.14, 11.41, 11.26, 11.46, 12.27, 12.11, 12.07, 12.0, 12.13, 12.17, 12.23,
                       12.1, 13.17]
    elif _type == 'aver':
        _type_index = 3.4
        format_data = [13.71, 13.68, 13.47, 13.22, 13.14, 13.17, 13.08, 12.67, 12.27, 11.6, 10.82, 10.45, 10.63, 10.88,
                       11.14, 11.13, 11.29, 11.33, 11.63, 11.42, 12.05, 12.72, 12.36, 12.29, 12.14, 12.25, 12.37, 12.61,
                       12.78, 13.99]
    elif _type == 'rate':
        _type_index = 8
        format_data = [0.51, -3.95, 0.22, -2.31, 0.76, -0.23, -1.97, -4.42, -0.97, -9.98, -4.27, 2.37, -2.04, 4.73,
                       1.99, -1.06, 1.88, 1.06, -0.61, 0.61, 10.01, -2.14, -1.7, 1.73, -1.7, 0.41, 2.87, -2.55, 9.97,
                       10.03]
    else:
        _type_index = 0
        format_data = []
        print('暂时不支持该类型')
    return _type_index, format_data
_type_index, format_data = get_format_data('rate')

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


def find_similar_data(his_list):
    data_list = []
    _max = len(his_list)
    for i in range(_max):
        if i + 30 < _max:
            his_rate_list = []
            for data in his_list[i:(i + 30)]:
                if isinstance(_type_index, float):
                    his_data = round((round(float(data.split(',')[3]), 2) + round(float(data.split(',')[4]), 2)) / 2, 2)
                else:
                    his_data = round(float(data.split(',')[_type_index]), 2)
                his_rate_list.append(his_data)

            data_list.append(his_rate_list)
    results = []
    for stock_data in data_list:
        stock_result = handle_dtw(format_data, stock_data)
        results.append(stock_result)

    best_stock_line = data_list[results.index(min(results))]
    return best_stock_line


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

    # similar_data = find_similar_data(his_list)
    # format_list.append(similar_data)

    high = []
    for info in his_list[-30:]:
        high.append(round(float(info.split(',')[3]), 2))
    print(high)

if __name__ == '__main__':
    # stocks = [
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
    # for stock_code in stocks:
    #     req_history_data(stock_code)
    # # print(format_list)
    #
    # new_format_data = []
    # for _index in range(30):
    #     _index_data_list = []
    #     for i in format_list:
    #         _index_data_list.append(i[_index])
    #     new_format_data.append(round(mean(_index_data_list), 2))
    #
    # print(new_format_data)
    req_history_data('000788')
