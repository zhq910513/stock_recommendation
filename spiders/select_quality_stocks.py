#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import pprint
from multiprocessing.pool import ThreadPool
import requests
from pylab import *

from common.log_out import log, log_err
from dbs.pipelines import MongoPipeline
from rules import r_updays_filter

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体（解决中文无法显示的问题）
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号“-”显示方块的问题
pp = pprint.PrettyPrinter(indent=4)

names = [
    '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'
]

format_data = [14.09, 13.78, 13.64, 13.43, 13.21, 13.17, 13.18, 13.08, 12.64, 12.32, 11.56, 10.8, 10.55, 10.63, 10.86, 11.16, 11.12, 11.28, 11.36, 11.55, 11.42, 12.12, 12.7, 12.34, 12.27, 12.14, 12.21, 12.38, 12.52, 12.78]

# 是否显示画图
show = True

# 是否入库
save = False

# 运行时间   每天下午18：00

# mongo db
db = 'stock'

# mongo collections
geguzhangfu = 'geguzhangfu'  # 个股涨幅
lianbang = 'lianbang' # 连榜
zhangting = 'zhangting' # 涨停
longhu_all = 'longhu_all'  # 总榜
longhu_capital = 'longhu_capital'  # 机构榜
longhu_org = 'longhu_org'  # 游资榜


class Stock:
    def __init__(self, collection, query):
        self.collection, self.query = collection, query
        self.stock_info_list = self.get_stocks()
        self.stock_history = self.thread_search()

    def get_stocks(self):
        hour_now = int(time.strftime("%H", time.localtime(time.time())))
        if hour_now >= 18:
            date_now = time.strftime("%Y%m%d", time.localtime(time.time()))
        else:
            date_now = time.strftime("%Y%m%d", time.localtime(time.time() - 86400))
        stock_info_list = []
        true_query = {'date': date_now}
        true_query.update(self.query)
        for data in MongoPipeline(self.collection).find(true_query):
            stock_info_list.append(data)
        return stock_info_list

    # 多线程处理数据
    def thread_search(self, remove_bad=True, Async=True):
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

    # 东方财富历史数据
    @staticmethod
    def req_history_data(stock_info):
        try:
            url = f'http://78.push2his.eastmoney.com/api/qt/stock/kline/get' \
                  f'?cb=jQuery' \
                  f'&secid=0.{stock_info["code"]}' \
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
            data = {
                'code': stock_info["code"],
                'limit_up_type': stock_info.get('limit_up_type'),
                'high_days': stock_info.get('high_days'),
                'name': stock_name,
                'history_data': his_data,
                'last_detail': last_detail
            }
            return data
        except Exception as error:
            log_err(error)

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
    def get_30_days_data(self, history_data, format_data=None):
        new_his_data = []
        for data in history_data[-30:]:
            sum_data = sum([float(data[1]), float(data[2]), float(data[3]), float(data[4])])
            new_his_data.append(round(sum_data/4, 2))
        return self.alignment_data(format_data, new_his_data)

    @staticmethod
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

    # 获取曲线相似度结果
    def get_result(self):
        if not self.stock_history:
            log('--- 获取龙虎榜失败 ---')
            return

        try:
            # 保存数据
            save_data = {'update_time': time.strftime("%Y-%m-%d", time.localtime(time.time()))}

            names = []
            results = []
            for stock_data in self.stock_history:
                stock_name = stock_data['name']
                stock_history_data = self.get_30_days_data(stock_data['history_data'], format_data)
                stock_result = self.cal_frechet_distance(np.array(format_data), np.array(stock_history_data))
                names.append(stock_name)
                results.append(stock_result)
            best_result = min(results)
            best_stock_name = names[results.index(best_result)]
            best_stock_his = []
            for stock_data in self.stock_history:
                if stock_data.get('name') == best_stock_name:
                    last_detail = stock_data['last_detail']
                    best_stock_his.append({
                        'name': stock_data['name'],
                        'history_data': self.get_30_days_data(stock_data['history_data'], format_data)
                    })

                    save_data.update({
                        'code': stock_data["code"],
                        'name': best_stock_name,
                        'limit_up_type': stock_data["limit_up_type"],
                        'high_days': stock_data["high_days"],
                        'match': round(float(best_result), 2)
                    })
                    save_data.update(last_detail)
                    log(f'本期最接近标准线的是：{stock_data["code"]} {best_stock_name}\n最后收盘信息：{last_detail}')

            # 画图
            if show:
                self.draw(format_data, best_stock_his)

            # save
            if save:
                MongoPipeline('daily_info').update_item({'update_time': None, 'code': None}, save_data)
        except Exception as error:
            log_err(error)

    # 画图
    @staticmethod
    def draw(format_data, stock_list):
        x = np.linspace(0, 1, 30)
        plt.figure()

        # 画标准数据线
        plt.plot(x, format_data, label='标准')

        # 画其他数据线
        for stock_data in stock_list:
            plt.plot(x, stock_data['history_data'], linestyle='--', label=stock_data['name'])

        plt.legend(loc=0)
        plt.show()


if __name__ == '__main__':
    for limit_query in [
        [lianbang, {"high_days" : r_updays_filter}],
        [zhangting, {"high_days" : '首板'}],
    ]:
        s = Stock(limit_query[0], limit_query[1])
        s.get_result()
