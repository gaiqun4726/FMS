# coding=utf-8
# from loader import InitialFDLoader
from datetime import timedelta
from preprocessor import PreProcessor

static_period = timedelta(seconds=30)


class Extractor(object):
    def __init__(self, processed_df):
        # self.initialFD = InitialFDLoader.getInitialFD()
        self.tagedSRCDataList = []
        self.processed_df = processed_df

    def extractSRC(self):
        item = WiFiData('a', 1, 2)
        srcList = [item]
        return srcList

    def findBestLocation(self, srcData):
        locationID = 1
        return locationID

    def getTagedSRCData(self, srcData):
        locationID = self.findBestLocation(srcData)
        tagedSRCData = TagedSRCData(srcData, locationID)
        return tagedSRCData

    def computePearsonCol(self, observeData, CalibrateData):
        pearsonCol = .0
        return pearsonCol

    def getTagedSRCDataList(self):
        srcList = self.extractSRC()
        for srcData in srcList:
            tagedSRCData = self.getTagedSRCData(srcData)
            self.tagedSRCDataList.append(tagedSRCData)
        return self.tagedSRCDataList


# 一个AP的Wi-Fi数据
class WiFiDataUnit(object):
    def __init__(self, ap_mac, rssi, channel):
        self.ap_mac = ap_mac
        self.rssi = rssi
        self.channel = channel


# 一个mu采集的所有AP的Wi-Fi数据
class WiFiDataList(object):
    def __init__(self, mu_mac):
        self.mu_mac = mu_mac
        self.fingerDataList = []

    def setFingerDataList(self, fingerDataList):
        self.fingerDataList = fingerDataList


# 静止状态信号特征
class SRCData(WiFiDataList):
    def __init__(self, mu_mac):
        WiFiDataList.__init__(self, mu_mac)


# 有位置标记的静止状态信号特征
class TagedSRCData(SRCData):
    def __init__(self, srcData, locationID):
        mu_mac = srcData.mu_mac
        SRCData.__init__(self, mu_mac)
        self.locationID = locationID
