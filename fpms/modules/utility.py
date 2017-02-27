#! /usr/bin/env python
# coding=utf-8

from datetime import timedelta
from dateutil.parser import parse
from sklearn.cluster import AffinityPropagation
import numpy as np
import pandas as pd


# (1)preprocessor文件使用
def countItems(infile, channel_dict):
    df = pd.read_csv(infile)
    index = df.index
    for i in index:
        ap_mac = df.ix[i, 'apmac']
        channel_dict[ap_mac] += 1
    return channel_dict


def whichFile(a, b, c):
    if a == b == c == 0:
        return -1
    if a > b and a > c:
        return 1
    elif b > a and b > c:
        return 2
    else:
        return 3


# (2)processor文件使用
def kalman_filter_method(data):
    n_iter = len(data)
    sz = (n_iter,)  # size of array
    z = data

    Q = 1e-5  # process variance
    # allocate space for arrays
    xhat = np.zeros(sz)  # a posteri estimate of x
    P = np.zeros(sz)  # a posteri error estimate
    xhatminus = np.zeros(sz)  # a priori estimate of x
    Pminus = np.zeros(sz)  # a priori error estimate
    K = np.zeros(sz)  # gain or blending factor

    R = 1 ** 2  # estimate of measurement variance, change to see effect

    # intial guesses
    xhat[0] = data[0]
    P[0] = 1.0

    for k in range(1, n_iter):
        # time update
        xhatminus[k] = xhat[k - 1]
        Pminus[k] = P[k - 1] + Q

        # measurement update
        K[k] = Pminus[k] / (Pminus[k] + R)
        xhat[k] = xhatminus[k] + K[k] * (z[k] - xhatminus[k])
        P[k] = (1 - K[k]) * Pminus[k]

    return xhat.round()


# 模式的时间是否超过5分钟, 每分钟采样次数是否超过6次
def time_period(start, end, length):
    delta = parse(end) - parse(start)
    if delta > timedelta(0, 300) and length > int(delta.seconds/10):
        return True
    else:
        return False


# 求得模式队列的均值
def get_mean(pattern, ap_list):
    res = {}
    for x in ap_list:
        res[x] = np.mean(pattern[x]).round()
    return res


# 生成输出模式串
def get_staticCharacters(values, ap_list):
    res = {}
    for x in ap_list:
        val = values[x]
        res[x] = val
    return res


# 对一个设备一天内的所有模式进行聚类
def all_patterns(X, outfile, ap):
    if len(X) < 2:
        out = pd.DataFrame(X,  columns=ap)
        out.to_csv(outfile)
        return
    af = AffinityPropagation().fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    clusters = [X[x] for x in cluster_centers_indices]
    out = pd.DataFrame(clusters, index=range(n_clusters_), columns=ap)
    out.to_csv(outfile)


# (3)generator文件使用
def parseIllegalId(infile):
    fh = open(infile)
    illegalList = [x.strip('\n') for x in fh]
    fh.close()
    res = []
    for tag in illegalList:
        seg = tag.split('_')
        res.append([int(seg[1]), int(seg[2])])
    return res


def formId(cords):
    a, b = cordsToId(cords)
    return 'g11_' + str(a) + '_' + str(b)


def idToCords(locID):
    id_x, id_y = locID
    return [4 * id_x + 2, 4 * id_y + 2]


def cordsToId(cords):
    x, y = cords
    return [int(x // 4), int(y // 4)]


def inIllegalRegion(infile, cords):
    ids = cordsToId(cords)
    illegalIds = parseIllegalId(infile)
    if ids in illegalIds:
        return True
    else:
        return False


def outOfBounds(cords):
    x, y = cords
    if x < 0 or x > 80 or y < 0 or y > 32:
        return True
    else:
        return False


def normalize(cords):
    return idToCords(cordsToId(cords))


def modifyCords(infile, cords):
    if inIllegalRegion(infile, cords) or outOfBounds(cords):
        x, y = cords
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                modifiedCords = [x + 4 * i, y + 4 * j]
                if not inIllegalRegion(infile, modifiedCords) and not outOfBounds(modifiedCords):
                    return normalize(modifiedCords)
        return [-10, -10]
    else:
        return normalize(cords)
