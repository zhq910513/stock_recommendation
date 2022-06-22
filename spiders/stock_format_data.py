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

    for info in his_list[-30:]:
        k_data(info.split(','))

def k_data(data_list):
    kp = round(float(data_list[1]), 2)
    sp = round(float(data_list[2]), 2)
    zg = round(float(data_list[3]), 2)
    zd = round(float(data_list[4]), 2)

    try:
        st = sp - kp # 阳线表示买方力量较强，卖方力量较弱，大量买单追逐使股价走高；阴线表示卖方力量较强，买方力量较弱，大量卖单抛压使股价走低。
        if st >= 0:
            st_status = '阳'
        else:
            st_status = '阴'
        syx = zg - sp  # 上影线越长，卖方抛压力量越大，股价上升的阻力也越大
        xyx = zd - sp  # 下影线越长，买单追逐的力量越强。投资者趁机购进股票，股价抗跌的能力就会增强
        if syx == 0:
            msg = '实体上部封顶'
        elif xyx == 0:
            msg = '实体下部封顶'
        else:
            msg = '“中”字形'

        print(f'{data_list[0]} 为 {st_status}线, 涨跌幅 {data_list[-3]}, 实体：{round(st,2)}, 上影线：{round(syx,2)}, 下影线：{round(xyx,2)}, {msg}')
    except Exception as error:
        print(error)

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
    req_history_data('000025')
