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

k_format_list = ['24cnn', '13nnn', '24nnk', '13kjn', '13nln', '24nlc', '24lcn', '24njn', '24kon', '24ncn', '13cnl', '13nlo', '24nkn', '13jnl', '24nll', '24llk', '13lkd', '24kdd', '13kno', '24dnn', '24nnn', '24nnl', '13lkl', '13ljn', '24nlk', '13kln', '24jnn', '13ono', '13ojg', '13gon', '13ndn', '13kgn', '13non', '24onl', '24lll', '24lld', '13dln', '24lnd', '13ndl', '13dll', '24nkg', '13kgc', '24gcd', '13lnn', '13kkl', '24kld', '24ldd', '13ddd', '24ddo', '13dod']


class Format:
    def req_history_data(self, stock_code):
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
        his_list = resp_data.get('klines')[-30:]

        success = 0
        failure = 0
        max_len = len(his_list)
        for num, data in enumerate(his_list):
            if 1 < num < (max_len - 1):
                font_2 = his_list[num - 2].split(',')
                font_1 = his_list[num - 1].split(',')
                data = data.split(',')
                status = self.k_data(font_2, font_1, data)
                if status:
                    success += 1
                else:
                    failure += 1
        print(f'预测成功率：{round(success / (success + failure), 2) * 100}%')

        # k_data(his_list[0].split(','), his_list[1].split(','), his_list[2].split(','))

    @staticmethod
    def analysis_k_data(data: list):
        kp = float(data[1])
        sp = float(data[2])
        zg = float(data[3])
        zd = float(data[4])
        zdf = float(sp - kp)
        format_status = {
            'a': '倒T字',
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
            'n': '大阴 双头 上影线',
            '0': '大阴 双头 下影线'
        }

        # 三天线状
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
                        status = f'[st!=0,zdf==0,syx==xyx]{data}'
                else:
                    if zdf > 0:
                        status = '强势 大 阳 线'
                    elif zdf < 0:
                        status = '强势 大 阴 线'
                    else:
                        status = f'[st!=0,syx==0,xyx!=0,zdf==0]{data}'
        except Exception as error:
            print(error)
        return status

    @staticmethod
    def analysis_cjl_data(font_2: list, font_1: list, data: list):
        font_2_cjl = round(float(font_2[5]), 2)
        font_1_cjl = round(float(font_1[5]), 2)
        data_cjl = round(float(data[5]), 2)

        # （本期的某个指标的值－上一期这个指标的值）／上一期这个指标的值
        font_1_rate = round(float((font_1_cjl - font_2_cjl) / font_2_cjl), 2)
        data_rate = round(float((data_cjl - font_1_cjl) / font_1_cjl), 2)
        if font_1_rate > data_rate:
            return '1'
        else:
            return '2'

    @staticmethod
    def analysis_hsl_data(font_2: list, font_1: list, data: list):
        font_2_hsl = round(float(font_2[10]), 2)
        font_1_hsl = round(float(font_1[10]), 2)
        data_hsl = round(float(data[10]), 2)

        # （本期的某个指标的值－上一期这个指标的值）／上一期这个指标的值
        font_1_rate = round(float((font_1_hsl - font_2_hsl) / font_2_hsl), 2)
        data_rate = round(float((data_hsl - font_1_hsl) / font_1_hsl), 2)
        if font_1_rate > data_rate:
            return '3'
        else:
            return '4'

    @staticmethod
    def prognosis(data):
        if data in k_format_list:
            return '涨'
        else:
            return ''


    def k_data(self, font_2: list, font_1: list, data: list):
        if not font_2 and not font_1:
            font_2_status = ''
            font_1_status = ''
        elif font_1 and not font_2:
            font_2_status = ''
            font_1_status = self.analysis_k_data(font_1)
        elif font_2:
            font_2_status = self.analysis_k_data(font_2)
            font_1_status = self.analysis_k_data(font_1)
        else:
            font_2_status = ''
            font_1_status = ''

        cjl_rate = self.analysis_cjl_data(font_2, font_1, data)
        hsl_rate = self.analysis_hsl_data(font_2, font_1, data)

        today_status = self.analysis_k_data(data)

        prognosis_data = str(cjl_rate) + str(hsl_rate) + str(font_2_status) + str(font_1_status) + str(today_status)
        prognosis_result = self.prognosis(prognosis_data)

        if float(data[8]) > 0:
            today_zd = '涨'
        else:
            today_zd = '跌'

        if today_zd == prognosis_result:
            return True
        else:
            return False


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

    f = Format()
    f.req_history_data('002339')
