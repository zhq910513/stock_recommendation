#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: stock_recommendation
@file: stock.py
@time: 2022/6/11 16:30
"""
import requests
import re,json
import pprint
pp=pprint.PrettyPrinter(indent=4)


def req_history_data(stock_code):
    url = f'http://51.push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery&secid=0.{stock_code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20220611&lmt=120'

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
    his_high = []
    for h in resp_data.get('klines')[-41:-11]:
        detail_data = h.split(',')
        print(detail_data)
        his_high.append(float(detail_data[3]))
    return stock_name, his_high

print(req_history_data('000025'))
