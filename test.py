import random
from multiprocessing.pool import ThreadPool

import matplotlib.pyplot as plt
import numpy as np

format_data = [float(j + random.choice([h for h in range(0, 9, 2)])) for j in range(3, 27, 2)]


# 对齐标准数据
def alignment_data(n, m):
    start = n[0]
    dis = start - m[0]
    new_list = []
    for x in m:
        new_list.append(x + dis)
    return new_list


# 获取最近10天交易数据
def get_10_days_data(stock_num):
    stock_name = ''
    stock_history_data = []
    stock_history_data = alignment_data(format_data, stock_history_data)
    return {'stock_name': stock_name, 'stock_history_data': stock_history_data}


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


# 画图
def draw(stock_list):
    x = np.linspace(0, 1, 12)
    plt.figure()
    plt.xlabel('X axis')
    plt.ylabel('Y axis')

    # 画标准数据线
    plt.plot(x, format_data)

    # 画其他数据线
    for stock_data in stock_list:
        plt.plot(x, stock_data['stock_history_data'], linestyle='--')
    plt.show()


# 获取曲线相似度结果
def get_result(stock_list=None):
    names = []
    results = []
    for stock_data in stock_list:
        stock_name = stock_data['stock_name']
        stock_history_data = stock_data['stock_history_data']
        stock_result = handle_dtw(format_data, stock_history_data)
        names.append(stock_name)
        results.append(stock_result)
    draw(stock_list)
    print(f'本期最接近标准线的是：{names[results.index(min(results))]}')


# 获取本期龙虎榜
def select_stocks():
    return []


# 多线程处理数据
def thread_search(remove_bad=False, Async=True):
    thread_list = []

    # 设置进程数
    pool = ThreadPool(processes=4)

    for info in select_stocks():
        if Async:
            out = pool.apply_async(func=get_10_days_data, args=(info,))  # 异步
        else:
            out = pool.apply(func=get_10_days_data, args=(info,))  # 同步
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


if __name__ == '__main__':
    stock_history = thread_search()
    get_result(stock_history)
