# coding=utf-8
# from loader import InitialFDLoader
from datetime import timedelta
from preprocessor import PreProcessor

static_period = timedelta(seconds=30)


# 更新数据提取类
class Extractor(object):
    def __init__(self, processedDf):
        # self.initialFD = InitialFDLoader.getInitialFD()
        self.tagedSRCDataList = []
        self.processedDf = processedDf

    # 提取静止状态信号特征
    def extractSRC(self):
        item = WiFiData('a', 1, 2)
        srcList = [item]
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
        return self.tagedSRCDataList


# 一个AP的Wi-Fi数据
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
