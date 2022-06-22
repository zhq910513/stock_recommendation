import numpy as np


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


if __name__ == '__main__':
    a_array = np.array([13.78, 13.66, 13.53, 13.52, 13.45, 13.43, 13.33, 13.22, 13.23, 13.15, 12.97, 12.88, 12.0,
                           11.9,
                           11.83, 11.66, 11.76, 11.95, 11.93, 11.94, 12.25, 12.18, 12.29, 12.58, 12.58, 12.61, 12.73,
                           12.91,
                           13.09, 13.57])
    b_array = np.array([1.72, 1.74, 1.74, 1.75, 1.76, 1.78, 1.76, 1.8, 1.8, 1.79, 1.83, 1.9, 1.88, 1.89, 1.9, 1.86, 1.88, 1.93, 1.9, 1.9, 1.91, 1.88, 1.9, 1.9, 1.91, 1.92, 1.91, 2.1, 2.31, 2.54])
    result_ab = cal_frechet_distance(a_array, b_array)
    print(result_ab)


