#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体（解决中文无法显示的问题）
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号“-”显示方块的问题


class Similarity(object):
    def __init__(self):
        self.format_data = [14.09, 13.78, 13.64, 13.43, 13.21, 13.17, 13.18, 13.08, 12.64, 12.32, 11.56, 10.8, 10.55,
                            10.63, 10.86, 11.16, 11.12, 11.28, 11.36, 11.55, 11.42, 12.12, 12.7, 12.34, 12.27, 12.14,
                            12.21, 12.38, 12.52, 12.78]

    # 对齐标准数据
    def alignment_data(self, m):
        n = self.format_data
        start = n[0]
        dis = start - m[0]
        new_list = []
        for x in m:
            new_list.append(round(float(x + dis), 2))
        return new_list

    # 计算相似度
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

    # 画图
    def draw(self, stock_info: dict):
        x = np.linspace(0, 1, 30)
        plt.figure()

        # 画标准数据线
        plt.plot(x, self.format_data, label='标准')

        # 画其他数据线
        stock_data = self.alignment_data(stock_info['history_data'])
        plt.plot(x, stock_data, linestyle='--', label=stock_info['name'])

        plt.legend(loc=0)
        plt.show()

    def run(self, data_list: list):
        new_data_list = self.alignment_data(data_list)
        return self.cal_frechet_distance(np.array(self.format_data), np.array(new_data_list))
