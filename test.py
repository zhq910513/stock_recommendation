#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: stock_recommendation
@file: stock_format_data.py
@time: 2022/6/11 16:30
"""
import json,copy
import pprint
import re
import time

import requests
from numpy import *

from spiders.longhubang import get_all_stocks

pp = pprint.PrettyPrinter(indent=4)

status_list = []

"""
十字线
大十字线
上影十字线
下影十字线

T字线
倒T字线

锤头线
倒锤头线

一字线

大阳线
大阳下影线（阳锤头线）
大阳上影线

小阳线
小阳上影线
小阳下影线

大阴线
大阴下影线
大阴上影线

小阴线
小阴上影线
小阴下影线
"""


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

    max_len = len(his_list)
    for num, data in enumerate(his_list):
        if 1 < num < (max_len-1):
            font_2 = his_list[num - 2].split(',')
            font_1 = his_list[num - 1].split(',')
            data = data.split(',')
            next_1 = his_list[num + 1].split(',')
            status = k_data(font_2, font_1, data, next_1)
            if status and status not in status_list:
                status_list.append(status)


def analysis_data(data:list):
    kp = float(data[1])
    sp = float(data[2])
    zg = float(data[3])
    zd = float(data[4])
    zdf = float(sp-kp)
    format_status = {
        'a':'倒T字',
        'b': 'T字',
        'c': '一字',
        'd': '大阳 短下影线',
        'e': '大阳 锤头线',
        'f': '大阴 短下影线',
        'g': '大阴 锤头线',
        'h': '大阳 短上影线',
        'i': '大阴 短上影线',
        'j': '双头大阳线',
        'k': '大阳 双头 上影线',
        'l': '大阳 双头 下影线',
        'm': '双头大阴线',
        'n':'大阴 双头 上影线',
        '0':'大阴 双头 下影线'
    }

    status = None
    try:
        st = abs(sp - kp)
        syx = abs(zg - sp)
        xyx = abs(zd - sp)

        if st == 0:
            if syx > 0 and xyx == 0:
                status = 'a'
            elif syx == 0 and xyx > 0:
                status = 'b'
            else:
                status = 'c'
        else:
            if syx != 0:
                syx_rate = round(syx / st, 2)
            else:
                syx_rate = 0
            if xyx != 0:
                xyx_rate = round(xyx / st, 2)
            else:
                xyx_rate = 0
            if syx == 0 and xyx != 0:
                if zdf > 0:
                    if xyx_rate > 0.3:
                        status = 'd'
                    else:
                        status = 'e'
                elif zdf < 0:
                    if xyx_rate > 0.3:
                        status = 'f'
                    else:
                        status = 'g'
                else:
                    # status = None
                    status = f'[st!=0,syx==0,xyx!=0,zdf==0]{data}'
            elif syx != 0 and xyx == 0:
                if zdf > 0:
                    if xyx_rate > 0.3:
                        status = 'h'
                    else:
                        status = 'e'
                elif zdf < 0:
                    if xyx_rate > 0.3:
                        status = 'i'
                    else:
                        status = 'g'
                else:
                    # status = None
                    status = f'[st!=0,syx!=0,xyx==0,zdf==0]{data}'
            elif syx != 0 and xyx != 0:
                if zdf > 0:
                    if syx_rate <= 0.3 and xyx <= 0.3:
                        status = 'j'
                    else:
                        if syx > xyx:
                            status = 'k'
                        else:
                            status = 'l'
                elif zdf < 0:
                    if syx_rate <= 0.3 and xyx <= 0.3:
                        status = 'm'
                    else:
                        if syx > xyx:
                            status = 'n'
                        else:
                            status = 'o'
                else:
                    # status = None
                    status = f'[st!=0,zdf==0,syx==xyx]{data}'
            else:
                if zdf > 0:
                    status = '强势 大 阳 线'
                elif zdf < 0:
                    status = '强势 大 阴 线'
                else:
                    # status = None
                    status = f'[st!=0,syx==0,xyx!=0,zdf==0]{data}'
    except Exception as error:
        print(error)
    return status


def k_data(font_2:list, font_1:list, data:list, next_1:list):
    font_2_status = analysis_data(font_2)
    font_1_status = analysis_data(font_1)
    today_status = analysis_data(data)
    next_status = float(next_1[8])

    if next_status > 0:
        if font_2_status and font_1_status and today_status:
            return font_2_status+font_1_status+today_status
        else:
            return None
    else:
        return None

if __name__ == '__main__':
    code_list = get_all_stocks('2022-06-23')
    for code in code_list:
        req_history_data(code)

    print(status_list)