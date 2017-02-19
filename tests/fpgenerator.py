# coding=utf-8

import pandas as pd
from pandas import Series, DataFrame
from datetime import datetime, date, timedelta

# 从位置信息文件中读取时间-位置数据
# df = pd.read_csv(r"E:\Graduation Project\finger data\loc-info.csv")
# size = len(df.index)
# for x in range(size):
#     series = df.iloc[x]
#     start = datetime.strptime(series['start'], '%Y-%m-%d %H:%M:%S')
#     end = datetime.strptime(series['end'], '%Y-%m-%d %H:%M:%S')
#     loc = series['locationID']
#     print(loc,end-start)

# 构建初始指纹库程序
mu_mac = 'B4-0B-44-2F-C8-A2'
loc_info = pd.read_csv(r"J:\G11_origin_data\2017-02-17\loc-info.csv")
finger_info = pd.read_csv(
    r"J:\demo\2017-02-17\merge_files" + '\\' + mu_mac + '.csv',
    header=None, names=['time', 'mac', 'rssi', 'channel', 'a', 'b', 'c', 'd', 'e', 'f'])
for i in list("abcdef"):
    del finger_info[i]
loc_dict = {}
str_format = '%Y-%m-%d %H:%M:%S:%f'
str_format2 = '%Y-%m-%d %H:%M:%S'
for x in range(len(loc_info.index)):
    series = loc_info.iloc[x]
    start = datetime.strptime(series['start'], str_format2) + timedelta(seconds=45)
    end = datetime.strptime(series['end'], str_format2) + timedelta(seconds=45)
    loc = series['locationID']
    loc_dict[loc] = (start, end)
finger_dict = {}
channel_times_dict = {}
ap_list = []
for x in range(len(finger_info.index)):
    series = finger_info.iloc[x]
    cur = datetime.strptime(series['time'], str_format)
    mac = series['mac']
    rssi = series['rssi']
    channel = series['channel']
    for key in loc_dict.keys():
        if loc_dict[key][0] <= cur <= loc_dict[key][1]:
            level1 = finger_dict.get(key, {})
            channel_level1 = channel_times_dict.get(key, {})
            if mac not in ap_list:
                ap_list.append(mac)
            level2 = level1.get(mac, [])
            channel_level2 = channel_level1.get(mac, {})
            level2.append((rssi, channel))
            channel_level3 = channel_level2.get(channel, 0) + 1
            channel_level2[channel] = channel_level3
            level1[mac] = level2
            channel_level1[mac] = channel_level2
            finger_dict[key] = level1
            channel_times_dict[key] = channel_level1
ap_list.sort()
for level1 in channel_times_dict.keys():
    level1_val = channel_times_dict[level1]
    for level2 in level1_val.keys():
        tmp = level1_val[level2]
        best_channel = 0
        best_times = 0
        for x in tmp.keys():
            if tmp[x] > best_times:
                best_times = tmp[x]
                best_channel = x
        level1_val[level2] = (best_channel, best_times)
for keys1 in finger_dict.keys():
    finger_val1 = finger_dict[keys1]
    channel_val1 = channel_times_dict[keys1]
    for keys2 in finger_val1.keys():
        finger_val2 = finger_val1[keys2]
        channel_val2 = channel_val1[keys2]
        sum_val = 0
        for rssi, channel in finger_val2:
            if channel == channel_val2[0]:
                sum_val += rssi
        val = round(sum_val / channel_val2[1])
        finger_val1[keys2] = val
df = DataFrame(finger_dict)
df = df.fillna(-100).T.sort_index(axis=1).sort_index()
df.index.name = "locationID"
df.to_csv(r'J:\demo\2017-02-17'+'\\'+mu_mac+'spectrum.csv')
