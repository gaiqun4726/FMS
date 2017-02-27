# coding=utf-8

import os

from preprocessor import PreProcessor
from loader import ResLoader
from utility import *

# from loader import InitialFDLoader

static_period = timedelta(seconds=30)


# 更新数据提取类
class Extractor(object):
    def __init__(self, muMac, processedDf, channelDf):
        # self.initialFD = InitialFDLoader.getInitialFD()
        self.muMac = muMac
        self.tagedSRCDataList = []
        self.processedDf = processedDf
        self.channelDf = channelDf

    # 提取静止状态信号特征
    def extractSRC(self):
        srcList = []
        apListPath = os.path.join(os.path.join(ResLoader.getRootPath(), ResLoader.getResourcePath()),
                                  ResLoader.getAPListPath())
        # 读取ap_list文件
        fh = open(apListPath)
        ap = fh.readlines()
        fh.close()
        ap = [x[:-1] for x in ap]  # 列表有序
        # 存放临时识别出的信号模式
        pattern = {}
        for value in ap:
            pattern[value] = []  # 字典无序
        # 读取kalman滤波后的数据
        df_kalman = self.processedDf
        index = df_kalman.index
        columns = df_kalman.columns
        start_index = index[0]
        for x in index:
            end_index = x
            for y in columns:
                value = df_kalman.ix[x, y]
                seq = pattern[y]
                if not seq:
                    seq.append(value)
                    pattern[y] = seq
                else:
                    if np.abs(np.mean(seq) - value) > 2 or np.abs(seq[-1] - value) > 2:
                        if time_period(start_index, end_index, len(seq)):
                            mean_values = get_mean(pattern, ap)
                            staticCharacters = get_staticCharacters(mean_values, ap)
                            wifiDataList = []
                            for apMac in staticCharacters.keys():
                                channel = self.channelDf.ix[start_index, apMac]
                                wifiDataUnit = WiFiDataUnit(apMac, staticCharacters[apMac], channel)
                                wifiDataList.append(wifiDataUnit)
                            srcData = SRCData(self.muMac)
                            srcData.setFingerDataList(wifiDataList)
                            srcList.append(srcData)
                        else:
                            keys = pattern.keys()
                            for key in keys:
                                pattern[key] = []
                        start_index = end_index
                    else:
                        seq.append(value)
                        pattern[y] = seq

        return srcList

    # 求得最佳位置标签
    def findBestLocation(self, srcData):
        locationID = 1
        return locationID

    # 返回标记后的更新数据
    def getTagedSRCData(self, srcData):
        locationID = self.findBestLocation(srcData)
        tagedSRCData = TagedSRCData(srcData, locationID)
        return tagedSRCData

    # 计算pearson相关系数
    def computePearsonCol(self, observeData, CalibrateData):
        pearsonCol = .0
        return pearsonCol

    # 返回标记更新数据列表
    def getTagedSRCDataList(self):
        srcList = self.extractSRC()
        for srcData in srcList:
            tagedSRCData = self.getTagedSRCData(srcData)
            self.tagedSRCDataList.append(tagedSRCData)
        return self.tagedSRCDataList  # 一个AP的Wi-Fi数据


class WiFiDataUnit(object):
    def __init__(self, apMac, rssi, channel):
        self.apMac = apMac
        self.rssi = rssi
        self.channel = channel


# 一个mu采集的所有AP的Wi-Fi数据
class WiFiDataList(object):
    def __init__(self, muMac):
        self.muMac = muMac
        self.fingerDataList = []

    def setFingerDataList(self, fingerDataList):
        self.fingerDataList = fingerDataList


# 静止状态信号特征
class SRCData(WiFiDataList):
    def __init__(self, muMac):
        WiFiDataList.__init__(self, muMac)


# 有位置标记的静止状态信号特征
class TagedSRCData(SRCData):
    def __init__(self, srcData, locationID):
        muMac = srcData.muMac
        SRCData.__init__(self, muMac)
        self.locationID = locationID


if __name__ == '__main__':
    preprocessor = PreProcessor('2017-01-17')
    muMac = 'B4-0B-44-2F-C8-A2'
    rssiDf, channelDf = preprocessor.loadData(muMac)
    extractor = Extractor(muMac, rssiDf, channelDf)
    print(extractor.extractSRC())
