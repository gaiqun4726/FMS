# coding=utf-8
import os, time
from Queue import Queue
from scipy.stats import mode
from pandas import DataFrame

from fpms.models import InitialFD
from loader import ResLoader
from utility import *

slideWindow = timedelta(minutes=1)
meanWindow = timedelta(milliseconds=500)


# 初始指纹库生成类
class InitialFDGenerator(object):
    def __init__(self):
        self.surveyMu = ResLoader.getCalibrateMuMac()
        self.sampleInfo = ResLoader.getSampleInfo()
        self.fingerOriginDataPath = ResLoader.getFingerOriginDataPath()
        self.fingerMergeFilePath = ResLoader.getFingerMergeDataPath()
        self.surveyMuFingerDataPath = os.path.join(self.fingerMergeFilePath, self.surveyMu + ".csv")

    # 构建初始指纹库方法
    def generateFD(self):
        loc_info = pd.read_csv(self.sampleInfo)
        finger_info = pd.read_csv(
            self.surveyMuFingerDataPath, header=None,
            names=['time', 'mac', 'rssi', 'channel', 'a', 'b', 'c', 'd', 'e', 'f'])
        for i in list("abcdef"):
            del finger_info[i]
        loc_dict = {}
        for x in range(len(loc_info.index)):
            series = loc_info.iloc[x]
            start = time.strptime(series['start'], '%Y-%m-%d %H:%M:%S')
            end = time.strptime(series['end'], '%Y-%m-%d %H:%M:%S')
            loc = series['locationID']
            loc_dict[loc] = (start, end)
        finger_dict = {}
        channel_times_dict = {}
        ap_list = []
        # 挑出最优信道
        for x in range(len(finger_info.index)):
            series = finger_info.iloc[x]
            cur = time.strptime(series['time'], '%Y-%m-%d %H:%M:%S')
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
        # 求最优信道的rssi均值
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
                finger_val1[keys2] = (val, channel_val2[0])
        # 清空原初始指纹库
        InitialFD.objects.all().delete()
        # 将初始指纹库存入数据库
        for keys1 in finger_dict.keys():
            val1 = finger_dict[keys1]
            for keys2 in val1.keys():
                rssi, channel = val1[keys2]
                item = InitialFD(locationID=keys1, apMAC=keys2, rssi=rssi, channel=channel)
                item.save()

    def mergeFiles(self):
        inpath = self.fingerOriginDataPath
        outpath = self.fingerMergeFilePath

        if not os.path.isdir(inpath):
            print("没有Wi-Fi探针采样数据！")
            return -1

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


# Wi-Fi探针数据预处理类
class PreProcessor(object):
    def __init__(self, dateTime):
        # self.ordinary_mu = ordinary_mu if ordinary_mu.__contains__('-') else ordinary_mu.replace(':', '-')
        self.dateTime = dateTime
        self.originDataPath = ResLoader.getOriginDataPath(self.dateTime)
        self.mergeFilePath = ResLoader.getMergeFilePath(self.dateTime)
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
        filePath = os.path.join(self.mergeFilePath, muMac + '.csv')
        headers = ['time', 'apmac', 'rssi', 'channel', 'isassociated', 'type', 'seq', 'frame', 'bssid', 'noise']
        dataDf = pd.read_csv(filePath, header=None, names=headers)
        collectWifiData = CollectWifiData(dataDf)
        return collectWifiData.getCollectWifiData()

    # 检查数据库中是否已经有初始指纹库
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
        self.rssiDf = ''  # 保存信号强度的DataFrame
        self.channelDf = ''  # 保存信道的DataFrame
        self.filterData()
        self.kalmanFilter()

    # 数据过滤，对一秒钟的所有数据，选择最佳信道，取均值
    def filterData(self):
        grouped1 = self.dataDf.groupby(['time', 'apmac'])['rssi'].apply(lambda x: x.mean())
        grouped2 = self.dataDf.groupby(['time', 'apmac'])['channel'].apply(lambda x: mode(x)[0][0])
        self.rssiDf = grouped1.unstack()
        self.channelDf = grouped2.unstack()

    # 对采样数据进行缺失值插补，然后进行滤波操作
    def kalmanFilter(self):
        global meanWindow
        self.rssiDf = self.rssiDf.sort_index()
        self.channelDf = self.channelDf.sort_index()
        self.rssiDf.fillna(method='bfill', axis=0, inplace=True)
        self.rssiDf.fillna(method='ffill', axis=0, inplace=True)
        self.channelDf.fillna(method='bfill', axis=0, inplace=True)
        self.channelDf.fillna(method='ffill', axis=0, inplace=True)
        # print(u'channel size:%d' % len(self.channelDf))
        index = self.rssiDf.index
        columns = self.rssiDf.columns
        arr = np.array(self.rssiDf)
        arr = arr.T
        newList = []
        for x in arr:
            newList.append(list(kalman_filter_method(x)))
        arr = np.array(newList).T
        df = DataFrame(arr)
        df.set_index(index)
        df.index = index
        df.columns = columns
        self.dataDf = df

    def getCollectWifiData(self):
        # print self.dataDf
        return self.dataDf, self.channelDf


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
    pp = PreProcessor('2017-01-17')
    print len(pp.loadData('00-0F-E2-F0-66-A0'))
