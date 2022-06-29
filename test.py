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

import requests
from pylab import *
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

f_l = [
    [13.78, 13.66, 13.53, 13.52, 13.45, 13.43, 13.33, 13.22, 13.23, 13.15, 12.97, 12.88, 12.0, 11.9, 11.83, 11.66, 11.76, 11.95, 11.93, 11.94, 12.25, 12.18, 12.29, 12.58, 12.58, 12.61, 12.73, 12.91, 13.09, 13.57],
    [11.33, 11.24, 11.25, 11.68, 11.76, 11.74, 11.46, 11.09, 10.12, 9.67, 8.75, 8.8, 8.82, 9.36, 9.75, 9.39, 9.46, 9.53, 10.36, 9.99, 10.33, 10.55, 10.4, 10.95, 10.7, 10.66, 11.51, 11.66, 10.88, 10.89],
    [10.6, 10.59, 10.5, 10.41, 10.46, 10.6, 10.55, 10.34, 9.97, 9.63, 8.9, 8.84, 8.75, 8.96, 9.2, 9.1, 9.26, 9.49, 9.91, 9.83, 9.85, 9.98, 9.93, 10.06, 10.16, 10.24, 10.29, 11.29, 11.78, 11.29],
    [6.66, 6.41, 6.39, 6.23, 6.21, 6.11, 6.13, 6.12, 6.08, 6.08, 6.05, 6.13, 6.05, 5.69, 5.56, 5.27, 5.28, 5.28, 5.39, 5.48, 5.38, 5.48, 5.53, 5.59, 5.54, 5.59, 5.7, 5.68, 5.84, 5.85],
    [4.9, 4.83, 4.7, 4.62, 4.7, 4.61, 4.36, 4.37, 4.5, 4.42, 4.22, 4.05, 3.94, 3.72, 3.54, 3.55, 3.65, 3.63, 3.55, 3.59, 3.54, 3.66, 3.54, 3.85, 3.8, 3.95, 4.05, 4.26, 4.55, 5.01],
    [6.35, 6.3, 6.14, 6.03, 5.87, 5.93, 5.91, 6.03, 6.11, 6.16, 6.04, 5.88, 5.74, 5.59, 5.24, 5.18, 5.2, 5.4, 5.39, 5.17, 5.24, 5.27, 5.49, 5.4, 5.53, 5.65, 5.59, 5.84, 5.78, 5.88],
    [5.6, 5.65, 5.45, 5.3, 5.19, 5.22, 5.17, 4.99, 5.15, 5.28, 5.2, 5.03, 4.8, 4.6, 4.3, 4.24, 4.35, 4.33, 4.42, 4.36, 4.4, 4.44, 4.53, 4.46, 4.59, 4.65, 4.68, 4.84, 4.86, 5.17]
               ]

format_data =     [14.29, 13.78, 13.81, 13.38, 13.31, 13.19, 13.2, 13.27, 12.88, 12.53, 12.05, 11.0, 10.52, 10.71, 10.65, 11.07, 11.05, 11.18, 11.28, 11.51, 11.36, 11.73, 13.0, 12.48, 12.14, 12.13, 12.15, 12.23, 12.63, 12.1]
new_format_data = [14.09, 13.78, 13.64, 13.43, 13.21, 13.17, 13.18, 13.08, 12.64, 12.32, 11.56, 10.8, 10.55, 10.63, 10.86, 11.16, 11.12, 11.28, 11.36, 11.55, 11.42, 12.12, 12.7, 12.34, 12.27, 12.14, 12.21, 12.38, 12.52, 12.78]
class Analysis:
    def __init__(self, his_data: str):
        self.k_format = {
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
        self.success = 0
        self.failure = 0

    def analysis_1d_data(self):
        pass

    def analysis_3d_data(self, font_2: list, font_1: list, font_0: list):
        pass

    def analysis_all_data(self):
        pass

    @staticmethod
    def analysis_k_link(data: list):
        kp = float(data[1])
        sp = float(data[2])
        zg = float(data[3])
        zd = float(data[4])
        zdf = float(sp - kp)

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

    f_data = []
    data_list = []
    for data in his_list[-53:-23]:
        print(data)
        data = data.split(',')[1:5]
        f_data.append(round(float(data[0]), 2))
        new_data = []
        for i in data:
            new_data.append(round(float(i), 2))
        data_list.append(round(sum(new_data)/4, 2))
    print(f_data)
    print(data_list)


def alignment_data(n, m):
    start = n[0]
    dis = start - m[0]
    new_list = []
    for x in m:
        new_list.append(round(float(x + dis), 2))
    return new_list


def cal_frechet_distance(curve_a: np.ndarray, curve_b: np.ndarray):
    # 距离公式，两个坐标作差，平方，累加后开根号
    def euc_dist(pt1, pt2):
        return np.sqrt(np.square(pt2[0] - pt1[0]) + np.square(pt2[1] - pt1[1]))

    # 用递归方式计算，遍历整个ca矩阵
    def _c(ca, i, j, P, Q):  # 从ca左上角开始计算，这里用堆的方法把计算序列从右下角压入到左上角，实际计算时是从左上角开始
        if ca[i, j] > -1:
            return ca[i, j]
        elif i == 0 and j == 0:  # 走到最左上角，只会计算一次
            ca[i, j] = euc_dist(P[0], Q[0])
        elif i > 0 and j == 0:  # 沿着Q的边边走
            ca[i, j] = max(_c(ca, i - 1, 0, P, Q), euc_dist(P[i], Q[0]))
        elif i == 0 and j > 0:  # 沿着P的边边走
            ca[i, j] = max(_c(ca, 0, j - 1, P, Q), euc_dist(P[0], Q[j]))
        elif i > 0 and j > 0:  # 核心代码：在ca矩阵中间走，寻找对齐路径
            ca[i, j] = max(min(_c(ca, i - 1, j, P, Q),  # 正上方
                               _c(ca, i - 1, j - 1, P, Q),  # 斜左上角
                               _c(ca, i, j - 1, P, Q)),  # 正左方
                           euc_dist(P[i], Q[j]))
        else:  # 非法的无效数据，算法中不考虑，此时 i<0,j<0
            ca[i, j] = float("inf")
        return ca[i, j]

    # 这个是给我们调用的方法
    def frechet_distance(P, Q):
        ca = np.ones((len(P), len(Q)))
        ca = np.multiply(ca, -1)
        dis = _c(ca, len(P) - 1, len(Q) - 1, P, Q)  # ca为全-1的矩阵，shape = ( len(a), len(b) )
        return dis

    # 这里构造计算序列
    curve_line_a = list(zip(range(len(curve_a)), curve_a))
    curve_line_b = list(zip(range(len(curve_b)), curve_b))
    return frechet_distance(curve_line_a, curve_line_b)


def draw(format_data, stock_list=None):
    x = np.linspace(0, 1, 30)
    plt.figure()

    # 画标准数据线
    plt.plot(x, format_data, label='format')

    # 画其他数据线
    # new_data_list = alignment_data(format_data, stock_list)
    plt.plot(x, stock_list, linestyle='--', label='000025')

    plt.legend(loc=0)
    plt.show()


if __name__ == '__main__':
    code_list = ['000025']
    # for code in code_list:
    #     req_history_data(code)

    draw(format_data, new_format_data)
