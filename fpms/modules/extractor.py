# coding=utf-8
# from loader import InitialFDLoader


class Extractor(object):
    def __init__(self):
        # self.initialFD = InitialFDLoader.getInitialFD()
        self.period = 30

    def extractStatic(self, processed_df):
        item = WiFiData('a', 1, 2)
        staticList = [item]
        return staticList

    def findBestPosition(self, wifiDataList):
        positionID = 1
        return positionID

    def getTagedData(self, staticList):
        tagedDict = {1: 'a'}
        return tagedDict


class WiFiData(object):
    def __init__(self, ap_mac, rssi, channel):
        self.ap_mac = ap_mac
        self.rssi = rssi
        self.channel = channel
