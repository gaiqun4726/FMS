# coding=utf-8
import os
from Queue import Queue
from datetime import datetime, timedelta

import pandas as pd

# from fpms.models import InitialFD
from loader import ResLoader

slideWindow = timedelta(minutes=1)
meanWindow = timedelta(milliseconds=500)


# 初始指纹库生成类
class InitialFDGenerator(object):
    def __init__(self, surveyMu, dateTime):
        self.surveyMu = surveyMu if surveyMu.__contains__('-') else surveyMu.replace(':', '-')
        self.rootPath = ResLoader.getRootPath()
        self.middleFilePath = os.path.join(self.rootPath, ResLoader.getMiddleFilePath())
        self.dateTime = dateTime
        self.dateFilePath = os.path.join(self.middleFilePath, self.dateTime)
        self.locInfoPath = os.path.join(self.dateFilePath, ResLoader.getLocInfoPath())
        self.mergeFilePath = os.path.join(self.dateFilePath, ResLoader.getMergeFilePath())
        self.fingerDataPath = os.path.join(os.path.join(self.mergeFilePath, self.surveyMu), '.csv')

        # 构建初始指纹库方法
        # def generateFD(self):
        #     loc_info = pd.read_csv(self.locInfoPath)
        #     finger_info = pd.read_csv(
        #         self.fingerDataPath, header=None, names=['time', 'mac', 'rssi', 'channel', 'a', 'b', 'c', 'd', 'e', 'f'])
        #     for i in list("abcdef"):
        #         del finger_info[i]
        #     loc_dict = {}
        #     for x in range(len(loc_info.index)):
        #         series = loc_info.iloc[x]
        #         start = datetime.strptime(series['start'], '%Y-%m-%d %H:%M:%S')
        #         end = datetime.strptime(series['end'], '%Y-%m-%d %H:%M:%S')
        #         loc = series['locationID']
        #         loc_dict[loc] = (start, end)
        #     finger_dict = {}
        #     channel_times_dict = {}
        #     ap_list = []
        #     # 挑出最优信道
        #     for x in range(len(finger_info.index)):
        #         series = finger_info.iloc[x]
        #         cur = datetime.strptime(series['time'], '%Y-%m-%d %H:%M:%S')
        #         mac = series['mac']
        #         rssi = series['rssi']
        #         channel = series['channel']
        #         for key in loc_dict.keys():
        #             if loc_dict[key][0] <= cur <= loc_dict[key][1]:
        #                 level1 = finger_dict.get(key, {})
        #                 channel_level1 = channel_times_dict.get(key, {})
        #                 if mac not in ap_list:
        #                     ap_list.append(mac)
        #                 level2 = level1.get(mac, [])
        #                 channel_level2 = channel_level1.get(mac, {})
        #                 level2.append((rssi, channel))
        #                 channel_level3 = channel_level2.get(channel, 0) + 1
        #                 channel_level2[channel] = channel_level3
        #                 level1[mac] = level2
        #                 channel_level1[mac] = channel_level2
        #                 finger_dict[key] = level1
        #                 channel_times_dict[key] = channel_level1
        #     ap_list.sort()
        #     # 求最优信道的rssi均值
        #     for level1 in channel_times_dict.keys():
        #         level1_val = channel_times_dict[level1]
        #         for level2 in level1_val.keys():
        #             tmp = level1_val[level2]
        #             best_channel = 0
        #             best_times = 0
        #             for x in tmp.keys():
        #                 if tmp[x] > best_times:
        #                     best_times = tmp[x]
        #                     best_channel = x
        #             level1_val[level2] = (best_channel, best_times)
        #     for keys1 in finger_dict.keys():
        #         finger_val1 = finger_dict[keys1]
        #         channel_val1 = channel_times_dict[keys1]
        #         for keys2 in finger_val1.keys():
        #             finger_val2 = finger_val1[keys2]
        #             channel_val2 = channel_val1[keys2]
        #             sum_val = 0
        #             for rssi, channel in finger_val2:
        #                 if channel == channel_val2[0]:
        #                     sum_val += rssi
        #             val = round(sum_val / channel_val2[1])
        #             finger_val1[keys2] = (val, channel_val2[0])
        #     # 清空原初始指纹库
        #     InitialFD.objects.all().delete()
        #     # 将初始指纹库存入数据库
        #     for keys1 in finger_dict.keys():
        #         val1 = finger_dict[keys1]
        #         for keys2 in val1.keys():
        #             rssi, channel = val1[keys2]
        #             item = InitialFD(locationID=keys1, apMAC=keys2, rssi=rssi, channel=channel)
        #             item.save()


# Wi-Fi探针数据预处理类
class PreProcessor(object):
    def __init__(self, dateTime):
        # self.ordinary_mu = ordinary_mu if ordinary_mu.__contains__('-') else ordinary_mu.replace(':', '-')
        self.dateTime = dateTime
        self.rootPath = ResLoader.getRootPath()
        self.originDataPath = os.path.join(os.path.join(self.rootPath, ResLoader.getOriginDataPath()),
                                           self.dateTime)
        self.middleFilePath = os.path.join(self.rootPath, ResLoader.getMiddleFilePath())
        self.dateFilePath = os.path.join(self.middleFilePath, self.dateTime)
        self.mergeFilePath = os.path.join(self.dateFilePath, ResLoader.getMergeFilePath())
        self.allMuSet = set()  # 保存一天之中所有mu的MAC地址的集合

    # 将采集数据按照MAC地址分类
    def mergeFiles(self):
        inpath = self.originDataPath
        outpath = self.mergeFilePath

        if not os.path.isdir(inpath):
            print(self.dateTime + "没有Wi-Fi探针数据记录！")
            return -1

        print("将探针数据按MAC地址分类--start")
        if not os.path.isdir(outpath):
            os.makedirs(outpath)

        for parent, dirnames, filenames in os.walk(inpath):
            for filename in filenames:
                fin = open(os.path.join(parent, filename).replace('\\', '\\\\'))
                dict_of_file = {}
                for line in fin:
                    seg = line.split(',')
                    muMac = seg[2].replace(':', '-')
                    del seg[2]
                    # 将ap剔除，保存mu
                    if int(seg[4]) == 1:
                        self.allMuSet.add(muMac)
                    line = ','.join(seg)
                    if muMac in dict_of_file:
                        dict_of_file[muMac].append(line)
                    else:
                        dict_of_file[muMac] = [line]
                fin.close()
                for block in dict_of_file:
                    try:
                        fout = open(outpath + '\\' + block + '.csv', 'a')
                        fout.writelines(dict_of_file[block])
                        fout.close()
                    except IOError:
                        print(block)
        print("将记录按MAC地址分类--end")
        print('采样周期内，所有连接系统内AP的MAC地址列表个数%d：\n' % len(self.allMuSet))

    # 载入一个mu全天的探针数据，并进行信道切换数据剔除、卡尔曼滤波等预处理操作
    def loadData(self, muMac):
        filePath = os.path.join(os.path.join(self.mergeFilePath, muMac), '.csv')
        dataDf = pd.read_csv(
            filePath, header=None,
            names=['timestamp', 'ap_mac', 'rssi', 'channel', 'a', 'b', 'c', 'd', 'e', 'f'])
        collectWifiData = CollectWifiData(dataDf)
        return collectWifiData.getCollectWifiData()

    def checkInitialFD(self):
        initialFD = []
        if initialFD == []:
            print('没有初始指纹库')
            return False
        else:
            return True


# 持有Wi-Fi探针数据的类
class CollectWifiData(object):
    def __init__(self, dataDf):
        self.dataDf = dataDf
        self.filterData()
        self.kalmanFilter()

    def filterData(self):
        global slideWindow
        self.dataDf = []

    def kalmanFilter(self):
        global meanWindow
        self.dataDf = []

    def getCollectWifiData(self):
        return self.dataDf


# class Decoder(object):
#     def __init__(self, listenerSocket):
#         self.buffered_queue = Queue()
#         self.listenerSocket = listenerSocket
#
#     def getDatagram(self):
#         datagram = self.listenerSocket.recv(1500)
#         self.buffered_queue.put(datagram)
#
#     def decodeMessage(self):
#         while True:
#             datagram = self.buffered_queue.get()
#         pass


if __name__ == '__main__':
    pp = PreProcessor('', '2017-01-17')
    print pp.mergeFiles()
