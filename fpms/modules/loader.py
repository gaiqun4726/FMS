# coding=utf-8

from xml.dom.minidom import parse
import xml.dom.minidom
import os
import json
import pandas as pd

from fpms.models import InitialFD, PartialFD, RegParameters, UpdateFD

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 从xml文件加载资源文件类
class ResLoader(object):
    __DOMTree = xml.dom.minidom.parse(os.path.join(BASE_DIR, "static/configs/resources.xml"))
    __collection = __DOMTree.documentElement

    @staticmethod
    def getRootPath():
        return ResLoader.__collection.getElementsByTagName("rootpath")[0].childNodes[0].data

    @staticmethod
    def getOriginDataPath(dateTime):
        rootPath = ResLoader.getRootPath()
        originDataPath = ResLoader.__collection.getElementsByTagName("origindatapath")[0].childNodes[0].data
        return os.path.join(os.path.join(rootPath, originDataPath), dateTime)

    @staticmethod
    def getMiddleFilePath():
        rootPath = ResLoader.getRootPath()
        middleFilePath = ResLoader.__collection.getElementsByTagName("middlefilepath")[0].childNodes[0].data
        return os.path.join(rootPath, middleFilePath)

    @staticmethod
    def getMergeFilePath(dateTime):
        middleFilePath = ResLoader.getMiddleFilePath()
        mergeFilePath = ResLoader.__collection.getElementsByTagName("mergefilepath")[0].childNodes[0].data
        return os.path.join(os.path.join(middleFilePath, dateTime), mergeFilePath)

    @staticmethod
    def getResourcePath():
        rootPath = ResLoader.getRootPath()
        resourcePath = ResLoader.__collection.getElementsByTagName("resourcepath")[0].childNodes[0].data
        return os.path.join(rootPath, resourcePath)

    @staticmethod
    def getApList():
        resourcePath = ResLoader.getResourcePath()
        apList = ResLoader.__collection.getElementsByTagName("aplist")[0].childNodes[0].data
        return os.path.join(resourcePath, apList)

    @staticmethod
    def getClusterResults():
        resourcePath = ResLoader.getResourcePath()
        clusterResults = ResLoader.__collection.getElementsByTagName("clusterresults")[0].childNodes[0].data
        return os.path.join(resourcePath, clusterResults)

    @staticmethod
    def getLocationCoordinates():
        resourcePath = ResLoader.getResourcePath()
        locationCoordinates = ResLoader.__collection.getElementsByTagName("locationcoordinates")[0].childNodes[0].data
        return os.path.join(resourcePath, locationCoordinates)

    @staticmethod
    def getSampleFingerDataPath():
        resourcePath = ResLoader.getResourcePath()
        fingerDataPath = ResLoader.__collection.getElementsByTagName("samplefingerdatapath")[0].childNodes[0].data
        return os.path.join(resourcePath, fingerDataPath)

    @staticmethod
    def getFingerOriginDataPath():
        sampleFingerDataPath = ResLoader.getSampleFingerDataPath()
        fingerOriginDataPath = ResLoader.__collection.getElementsByTagName("fingerorigindatapath")[0].childNodes[0].data
        return os.path.join(sampleFingerDataPath, fingerOriginDataPath)

    @staticmethod
    def getFingerMergeDataPath():
        sampleFingerDataPath = ResLoader.getSampleFingerDataPath()
        fingerMergeDataPath = ResLoader.__collection.getElementsByTagName("fingermergedatapath")[0].childNodes[0].data
        return os.path.join(sampleFingerDataPath, fingerMergeDataPath)

    @staticmethod
    def getSampleInfo():
        sampleFingerDataPath = ResLoader.getSampleFingerDataPath()
        sampleInfo = ResLoader.__collection.getElementsByTagName("sampleinfo")[0].childNodes[0].data
        return os.path.join(sampleFingerDataPath, sampleInfo)

    @staticmethod
    def getRegressionTrainSetPath():
        resourcePath = ResLoader.getResourcePath()
        regressionTrainSetPath = ResLoader.__collection.getElementsByTagName("regressiontrainsetpath")[0].childNodes[
            0].data
        return os.path.join(resourcePath, regressionTrainSetPath)

    @staticmethod
    def getPartialFDHistoryDataPath():
        resourcePath = ResLoader.getResourcePath()
        partialFDHistoryDataPath = \
            ResLoader.__collection.getElementsByTagName("partialfdhistorydatapath")[0].childNodes[
                0].data
        return os.path.join(resourcePath, partialFDHistoryDataPath)

    @staticmethod
    def getCalibrateMuMac():
        calibrateMuMac = ResLoader.__collection.getElementsByTagName("calibratemumac")[0].childNodes[0].data
        return calibrateMuMac


# 从数据库加载初始指纹库类
class InitialFDLoader(object):
    @staticmethod
    def getInitialFD():
        objects = InitialFD.objects.all()
        if objects.count() == 0:
            print(u'初始指纹库记录条数为0')
        fd_dict = {}
        for item in objects:
            locationID = item.locationID
            apMAC = item.apMAC
            rssi = item.rssi
            channel = item.channel
            level1 = fd_dict.get(locationID, {})
            level1[apMAC] = {'rssi': rssi, 'channel': channel}
            fd_dict[locationID] = level1
        return fd_dict


# 部分更新指纹库和回归系数表始终在变化，所以不能使用静态方法从数据库中读取数据

# 从数据库加载部分更新指纹库类
class PartialFDLoader(object):
    def getPartialFD(self):
        objects = PartialFD.objects.all()
        if objects.count() == 0:
            print(u'部分更新指纹库记录条数为0')
        fd_dict = {}
        for item in objects:
            locationID = item.locationID
            apMAC = item.apMAC
            rssi = item.rssi
            channel = item.channel
            historyDataPath = item.historyDataPath
            level1 = fd_dict.get(locationID, {})
            level1[apMAC] = {'rssi': rssi, 'channel': channel, 'historyDataPath': historyDataPath}
            fd_dict[locationID] = level1
        return fd_dict


# 从数据库加载回归系数表类
class ParameterLoader(object):
    def getParameter(self, muMac):
        objects = RegParameters.objects.filter(commonMU=muMac)
        if objects.count() == 0:
            return -1
        item = objects[0]
        surveyMU = item.surveyMU
        commonMU = item.commonMU
        a = item.a
        b = item.b
        Q = item.Q
        parameterUsability = item.parameterUsability
        trainSetPath = item.trainSetPath
        para_dict = {'surveyMU': surveyMU, 'commonMU': commonMU, 'a': a, 'b': b, 'Q': Q,
                     'parameterUsability': parameterUsability, 'trainSetPath': trainSetPath}
        return para_dict


# 根据生成日期，查找更新指纹库
class UpdateFDLoader(object):
    def getUpdateFD(self, dateTime):
        objects = UpdateFD.objects.filter(dateTime=dateTime)
        if objects.count() == 0:
            print(u'%s 这一天没有更新指纹库生成' % dateTime)
        fd_dict = {}
        for item in objects:
            locationID = item.locationID
            apMAC = item.apMAC
            rssi = item.rssi
            channel = item.channel
            level1 = fd_dict.get(locationID, {})
            level1[apMAC] = {'rssi': rssi, 'channel': channel}
            fd_dict[locationID] = level1
        return fd_dict


# 加载参考点空间聚类结果
class ClusterResultsLoader(object):
    @staticmethod
    def getClusterResults():
        path = ResLoader.getClusterResults()
        with open(path, 'r') as f:
            clusterToLocationDict = json.load(f)
        locationToClusterDict = {}
        keys = clusterToLocationDict.keys()
        for cls in keys:
            locationList = clusterToLocationDict.get(cls)
            for locationID in locationList:
                locationToClusterDict[locationID] = cls
        return clusterToLocationDict, locationToClusterDict


# 从csv文件中加载指纹库
class SpectrumLoader(object):
    path = r"L:\Graduation Project\finger data\middleFile\2017-01-20\B4-0B-44-2F-C8-A2spectrum.csv"

    # 从指纹库的csv文件加载指纹库字典
    def loadSpectrum(self):
        df = pd.read_csv(self.path, index_col='locationID')
        spectrumDict = {}
        for key1 in df.index:
            sr = df.ix[key1]
            lv2val = {}
            for key2 in sr.index:
                lv2val[key2] = [sr[key2], ]
            spectrumDict[key1] = lv2val
        return spectrumDict
