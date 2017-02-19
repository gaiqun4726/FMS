# coding=utf-8
# 从指纹库中，提取一个AP的所有信号强度，并按照空间位置组织成信号矩阵
# from pandas import Series, DataFrame
# import numpy as np
# import pandas as pd
#
# df = pd.read_csv(r"J:\demo\2016-12-30\results\spectrum.csv")
# df = df[['locationID', '74:1F:4A:C8:9F:80']]
# res = np.zeros((8, 20)) + -100
# for d in df.index:
#     sr = df.ix[d]
#     #     print sr
#     a, b, c = sr['locationID'].split('_')
#     if int(b) >= 20 or int(c) >= 8:
#         continue
#     val = sr['74:1F:4A:C8:9F:80']
#     try:
#         row = str(7 - int(c))
#         col = b
#         res[row, col] = val
#     except:
#         print b, c
# print res

# 计算并绘制Wi-Fi探针的采样频率直方图，效果不好，pass
# from datetime import datetime
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
#
# inpath = r"J:\G11_origin_data\2017-02-14\2017-02-14-14-59.csv"
# ll = list('abcdefghijk')
# df = pd.read_csv(inpath,names=ll)
#
# df = df[df['c'] == 'B4:0B:44:2F:C8:A2']
# df.sort_index(by='h')
# print len(df)
# time_gap = []
#
# first = datetime.strptime(df.ix[df.index[0],'a'],"%Y-%m-%d %H:%M:%S:%f")
# for x in df.index[1:]:
#     second = datetime.strptime(df.ix[x,'a'],"%Y-%m-%d %H:%M:%S:%f")
#     normal_day = datetime.strptime('2000-01-01',"%Y-%m-%d")
#     normal_day = normal_day + (second-first)
#     first = second
#     time_str = datetime.strftime(normal_day,"%Y:%m:%d:%H:%M:%S:%f")
#     time_list = time_str.split(':')
#     time_gap.append(1000*int(time_list[-2])+int(time_list[-1])/1000)
# # print time_gap
# time_gap = [x for x in time_gap if x>800 and x<2000]
# sns.distplot(time_gap,bins=20,kde=False)
# plt.show()

