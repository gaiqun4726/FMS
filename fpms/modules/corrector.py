# coding=utf-8

import os
import pickle

from loader import InitialFDLoader, PartialFDLoader, ParameterLoader, ResLoader
from extractor import TagedSRCData
from fpms.models import RegParameters

standardQ = .3


# 设备信号差异性校正类
class Corrector(object):
    # def __init__(self, tagedDict):
    #     self.initialFD = InitialFDLoader.getInitialFD()
    #     self.parameter = ''
    #     self.tagedDict = tagedDict
    #
    # def updatePara(self):
    #     parameter = ParameterLoader.getParameter()
    #     pass
    #
    # def loadPara(self):
    #     self.parameter = ParameterLoader.getParameter()
    #     pass
    #
    # def removeDiff(self):
    #     pass
    #
    # def updatePartialFD(self, modifiedDict):
    #     partialFD = PartialFDLoader.getPartialFD()
    #     pass
    def __init__(self, muMac, tagedSRCDataList):
        self.muMac = muMac
        self.parameterUsability = False
        self.parameterDict = []
        self.tagedSRCDataList = tagedSRCDataList
        self.updateDataList = []

    # 将更新数据校正后，返回更新数据列表
    def getUpdateDataList(self):
        rp = RegeressionPar(self.muMac, self.tagedSRCDataList)
        self.parameterUsability = rp.hasParameter()
        if self.parameterUsability is True:
            self.parameterDict = rp.getParameter()
            for tagedSRCData in self.tagedSRCDataList:
                updateData = self.removeDiff(tagedSRCData)
                self.updateDataList.append(updateData)

        return self.updateDataList

    # 剔除设备信号差异性
    def removeDiff(self, tagedSRCData):
        # 利用回归方程剔除设备信号差异性
        locationID = tagedSRCData.locationID
        fingerDataList = []
        updateData = TagedSRCData(self.muMac, locationID)
        updateData.setFingerDataList(fingerDataList)
        return updateData


# merge更新数据到部分更新指纹库类
class MergeData(object):
    def __init__(self):
        self.partialFD = {}
        self.partialFDHistoryData = {}

    # 将更新数据存入部分更新指纹库的历史数据，等待日后merge，取均值
    def mergeDataToPartialFD(self, updateDataList):
        for updateData in updateDataList:
            locationID = updateData.locationID
            historyData = self.partialFDHistoryData.get(locationID, [])
            historyData.append(updateData.fingerDataList)
            self.partialFDHistoryData[locationID] = historyData
            # 将部分更新指纹库及历史数据存入数据库和本地文件


# 自动更新回归系数表类
class RegeressionPar(object):
    global standardQ

    def __init__(self, muMac, tagedSRCDataList):
        self.muMac = muMac
        self.tagedSRCDataList = tagedSRCDataList
        self.initialFD = InitialFDLoader.getInitialFD()
        self.parameterDict = {}
        self.trainDataList = []
        self.parameterUsability = False
        self.autoUpdate()

    # 是否已经可以使用回归系数
    def hasParameter(self):
        return self.parameterUsability

    # 返回回归系数
    def getParameter(self):
        return self.parameterDict

    # 自动判断回归系数表是否需要更新
    def autoUpdate(self):
        self.loadDataBaseData()
        self.setDataBaseData()

    # 从数据库读取回归系数表记录
    def loadDataBaseData(self):
        parameterLoader = ParameterLoader()
        self.parameterDict = parameterLoader.getParameter(self.muMac)
        if self.parameterDict != -1:
            trainDataPath = os.path.join(ResLoader.getRegressionTrainSetPath(), self.parameterDict['trainSetPath'])
            self.trainDataList = []
            with open(trainDataPath, "rb") as trainDataFile:
                try:
                    while True:
                        trainData = pickle.load(trainDataFile)
                        self.trainDataList.append(trainData)
                except EOFError:
                    pass

    # 重新设置回归系数表，主要是添加训练数据或清空训练数据
    def setDataBaseData(self):
        if self.parameterDict != -1:
            surveyMU = self.parameterDict['surveyMU']
            commonMU = self.parameterDict['commonMU']
            a = self.parameterDict['a']
            b = self.parameterDict['b']
            Q = self.parameterDict['Q']
            parameterUsability = self.parameterDict['parameterUsability']
            trainSetPath = self.parameterDict['trainSetPath']

            self.parameterUsability = parameterUsability

            # 如果满足产生计算的条件，本次计算也不更改内存中的系数，在下一次读取时再改变系数
            if Q < standardQ:
                self.trainDataList.extend(self.tagedSRCDataList)
                # 将原来的系数、Q和训练数据存入数据库
                # 计算Q的业务逻辑
                Q = self.computeQ(self.trainDataList)
            else:
                newParameterDict = self.computeParameter()
                a = newParameterDict['a']
                b = newParameterDict['b']
                # 将Q和训练数据清空
                self.trainDataList = self.tagedSRCDataList
                Q = self.computeQ(self.trainDataList)
                # 将新的系数、Q、训练数据存入数据库
                parameterUsability = True
            output = open(trainSetPath, 'wb')
            for item in self.trainDataList:
                pickle.dump(item, output, -1)
            output.close()
            record = RegParameters(surveyMU=surveyMU, commonMU=commonMU, a=a, b=b, Q=Q,
                                   parameterUsability=parameterUsability, trainSetPath=trainSetPath)
            record.save()
        else:
            path = os.path.join(ResLoader.getRegressionTrainSetPath(), self.muMac)
            output = open(path, 'wb')
            for item in self.tagedSRCDataList:
                pickle.dump(item, output, -1)
            output.close()
            Q = self.computeQ(self.tagedSRCDataList)
            record = RegParameters(surveyMU=ResLoader.getCalibrateMuMac(), commonMU=self.muMac, a=0, b=0, Q=Q,
                                   parameterUsability=False, trainSetPath=self.muMac)
            record.save()

    # 使用训练数据构建线性回归方程，并求解回归方程的回归系数
    def computeParameter(self):
        # fd_dict = InitialFDLoader.getInitialFD()
        # self.trainDataList
        newParameterDict = {}
        return newParameterDict

    # 计算信号强度分布占比Q
    def computeQ(self, trainDataList):
        Q = 0
        return Q
