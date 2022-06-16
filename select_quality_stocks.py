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

# 是否显示画图
show = False

# 龙虎榜cookie   http://data.10jqka.com.cn/rank/lxsz/field/lxts/order/asc/page/1/ajax/1/free/1/
Cookie = 'v=A_rNEfcQTN_Nt8Cz2YuJ2fZvSysZq36F8C_yKQTzpg1Y95SV7DvOlcC_QjjX'


class Stock:
    def __init__(self):
        self.stock_info_list = self.select_stocks()
        self.stock_history = self.thread_search()

    # 标准数据类型   high   low   aver   rate
    @staticmethod
    def get_format_data(index_type):
        if index_type == 'high':
            _type_index = 3
            format_data = [13.78, 13.66, 13.53, 13.52, 13.45, 13.43, 13.33, 13.22, 13.23, 13.15, 12.97, 12.88, 12.0,
                           11.9,
                           11.83, 11.66, 11.76, 11.95, 11.93, 11.94, 12.25, 12.18, 12.29, 12.58, 12.58, 12.61, 12.73,
                           12.91,
                           13.09, 13.57]
        elif index_type == 'low':
            _type_index = 4
            format_data = [12.76, 12.9, 12.85, 12.86, 12.85, 12.92, 12.76, 12.71, 12.62, 12.44, 12.46, 12.36, 12.16,
                           12.12,
                           11.24, 11.29, 11.19, 11.26, 11.42, 11.41, 11.55, 11.72, 11.63, 11.68, 11.9, 12.06, 12.09,
                           12.36,
                           12.4, 12.72]
        elif index_type == 'aver':
            _type_index = 3.4
            format_data = [13.35, 13.4, 13.25, 13.12, 13.02, 13.0, 12.92, 12.78, 12.86, 12.76, 12.62, 12.59, 11.66,
                           11.62,
                           11.59, 11.69, 11.86, 11.98, 11.86, 11.82, 12.1, 12.0, 12.06, 12.4, 12.46, 12.62, 12.49, 12.8,
                           12.94, 13.2]
        elif index_type == 'rate':
            _type_index = 8
            format_data = [-0.17, -1.7, -0.72, -0.36, -1.1, 0.65, -0.19, -0.18, -0.24, -0.63, -1.28, 1.52, -1.06, -0.28,
                           1.38, -0.33, 1.55, 0.56, 0.76, -1.02, 3.15, 0.56, 1.64, -0.55, 0.88, 2.4, 0.38, 1.52, 4.04,
                           8.39]
        else:
            _type_index = 0
            format_data = []
            print('暂时不支持该类型')
        return _type_index, format_data

    # 多线程处理数据
    def thread_search(self, remove_bad=False, Async=True):
        thread_list = []

        # 设置进程数
        pool = ThreadPool(processes=4)

        for info in self.stock_info_list:
            if Async:
                out = pool.apply_async(func=self.req_history_data, args=(info,))  # 异步
            else:
                out = pool.apply(func=self.req_history_data, args=(info,))  # 同步
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

    # 获取本期龙虎榜
    def select_stocks(self):
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
        return self.req_longhu_stocks()

    # 龙虎榜数据
    @staticmethod
    def req_longhu_stocks():
        url = 'http://data.10jqka.com.cn/rank/lxsz/field/lxts/order/asc/page/1/ajax/1/free/1/'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': Cookie,
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
                    trade = tr.find_all('td')[9].get_text()
                    if int(up_days) <= 3 and str(stock_code).startswith('00') and '退' not in str(tr):
                        stocks.append({
                            'stock_code': stock_code,
                            'up_days': up_days,
                            'stock_trade': trade
                        })
                except:
                    pass
            return stocks
        except Exception as error:
            print(error)

    # 东方财富历史数据
    @staticmethod
    def req_history_data(stock_info):
        url = f'http://78.push2his.eastmoney.com/api/qt/stock/kline/get' \
              f'?cb=jQuery' \
              f'&secid=0.{stock_info["stock_code"]}' \
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
        his_data = []
        for h in resp_data.get('klines')[-30:]:
            his_data.append(h.split(','))
        last_price = resp_data.get('klines')[-1].split(',')
        last_detail = dict(zip(names, last_price))
        return {
            'stock_code': stock_info["stock_code"],
            'stock_trade': stock_info["stock_trade"],
            'up_days': stock_info["up_days"],
            'stock_name': stock_name,
            'stock_history_data': his_data,
            'last_detail': last_detail
        }

    # 对齐标准数据
    @staticmethod
    def alignment_data(n, m):
        start = n[0]
        dis = start - m[0]
        new_list = []
        for x in m:
            new_list.append(round(float(x + dis), 2))
        return new_list

    # 获取最近30天交易数据
    def get_30_days_data(self, _index, history_data, format_data):
        new_his_data = []
        for data in history_data[-30:]:
            if isinstance(_index, float):
                new_his_data.append(round((float(data[3]) + float(data[4])) / 2, 2))
            else:
                new_his_data.append(round(float(data[_index]), 2))
        return self.alignment_data(format_data, new_his_data)

    # 相似度计算
    @staticmethod
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

    # 获取曲线相似度结果
    def get_result(self):
        if not self.stock_history:
            print('--- 获取龙虎榜失败 ---')
            return

        for index_type in [
            'high',
            'low',
            'aver',
            'rate'
        ]:
            # 保存数据
            save_data = {'update_time': time.strftime("%Y-%m-%d", time.localtime(time.time())),
                         'stock_info_list': self.stock_info_list}
            _type_index, format_data = self.get_format_data(index_type)

            names = []
            results = []
            for stock_data in self.stock_history:
                stock_name = stock_data['stock_name']
                stock_history_data = self.get_30_days_data(_type_index, stock_data['stock_history_data'], format_data)
                stock_result = self.handle_dtw(format_data, stock_history_data)
                names.append(stock_name)
                results.append(stock_result)
            best_stock_name = names[results.index(min(results))]
            best_stock_his = []
            for stock_data in self.stock_history:
                if stock_data.get('stock_name') == best_stock_name:
                    last_detail = stock_data['last_detail']
                    best_stock_his.append({
                        'stock_name': stock_data['stock_name'],
                        'stock_history_data': self.get_30_days_data(_type_index, stock_data['stock_history_data'], format_data)
                    })
                    save_data.update({
                        'best_stock_code': stock_data["stock_code"],
                        'best_stock_name': best_stock_name,
                        'trade': stock_data["stock_trade"],
                        'up_days': stock_data["up_days"],
                        'type': [index_type]
                    })
                    save_data.update(last_detail)
                    print(f'本期最接近标准线的是：{stock_data["stock_code"]} {best_stock_name}\n最后收盘信息：{last_detail}')

            # 画图
            if show:
                self.draw(format_data, best_stock_his)

            # save
            MongoPipeline('daily_info').update_item({'update_time': None, 'best_stock_code': None}, save_data)

    # 画图
    @staticmethod
    def draw(format_data, stock_list):
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
    s = Stock()
    s.get_result()