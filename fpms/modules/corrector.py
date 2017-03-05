# coding=utf-8

import os
import pickle
import numpy as np
import traceback
from sklearn import linear_model

from loader import InitialFDLoader, PartialFDLoader, ParameterLoader, ResLoader
from extractor import TagedSRCData
from fpms.models import RegParameters, PartialFD

standardQ = 0.3


# 设备信号差异性校正类
class Corrector(object):
    def __init__(self, muMac, tagedSRCDataList):
        self.muMac = muMac
        self.parameterUsability = False
        self.parameterDict = {}
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
        else:
            self.updateDataList = self.tagedSRCDataList
        return self.updateDataList

    # 剔除设备信号差异性
    def removeDiff(self, tagedSRCData):
        # 利用回归方程剔除设备信号差异性
        fingerDataList = tagedSRCData.getFingerDataList()
        a = self.parameterDict['a']
        b = self.parameterDict['b']
        for item in fingerDataList:
            rssi = item.rssi
            newRssi = a * rssi + b
            item.rssi = newRssi
        tagedSRCData.setFingerDataList(fingerDataList)
        return tagedSRCData


# merge更新数据到部分更新指纹库类
class MergeData(object):
    def __init__(self):
        partialFDLoader = PartialFDLoader()
        self.partialFD = partialFDLoader.getPartialFD()

    # 将更新数据存入部分更新指纹库的历史数据，等待日后merge，取均值
    def mergeDataToPartialFD(self, updateDataList):
        for updateData in updateDataList:
            locationID = updateData.locationID
            # if locationID == '0' or locationID == 0:
            #     pass
            if locationID in self.partialFD.keys():
                for item in updateData.getFingerDataList():
                    apMac = item.apMac
                    if item.rssi != 0:
                        if apMac in self.partialFD[locationID].keys():
                            historyDataPath = os.path.join(ResLoader.getPartialFDHistoryDataPath(),
                                                           self.partialFD[locationID][apMac]['historyDataPath'])
                            historyDataList = []
                            with open(historyDataPath, "rb") as historyDataFile:
                                try:
                                    while True:
                                        historyData = pickle.load(historyDataFile)
                                        historyDataList.append(historyData)
                                except EOFError:
                                    pass
                            historyDataList.append(item)
                            output = open(historyDataPath, 'wb')
                            for item2 in historyDataList:
                                pickle.dump(item2, output, -1)
                            output.close()
                        else:
                            fileName = str(locationID) + '_' + item.apMac.replace(':', '-')
                            path = os.path.join(ResLoader.getPartialFDHistoryDataPath(), fileName)
                            output = open(path, 'wb')
                            pickle.dump(item, output, -1)
                            output.close()
                            partialFD = PartialFD(locationID=locationID, apMAC=item.apMac, rssi=item.rssi,
                                                  channel=item.channel, historyDataPath=fileName)
                            partialFD.save()
            else:
                for item in updateData.getFingerDataList():
                    if item.rssi != 0:
                        fileName = str(locationID) + '_' + item.apMac.replace(':', '-')
                        path = os.path.join(ResLoader.getPartialFDHistoryDataPath(), fileName)
                        output = open(path, 'wb')
                        pickle.dump(item, output, -1)
                        output.close()
                        partialFD = PartialFD(locationID=locationID, apMAC=item.apMac, rssi=item.rssi,
                                              channel=item.channel, historyDataPath=fileName)
                        partialFD.save()


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
            path = os.path.join(ResLoader.getRegressionTrainSetPath(), trainSetPath)
            output = open(path, 'wb')
            for item in self.trainDataList:
                pickle.dump(item, output, -1)
            output.close()
            record = RegParameters.objects.filter(surveyMU=surveyMU, commonMU=commonMU)
            record.update(a=a, b=b, Q=Q,
                          parameterUsability=parameterUsability, trainSetPath=trainSetPath)
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
        fd_dict = InitialFDLoader.getInitialFD()
        train_X = []
        train_Y = []
        for item in self.trainDataList:
            locationID = item.locationID
            fingerDataList = item.getFingerDataList()
            if locationID in fd_dict.keys():
                for item2 in fingerDataList:
                    o_apMac = item2.apMac
                    o_rssi = item2.rssi
                    o_channel = item2.channel
                    try:
                        tmp = fd_dict.get(locationID, {})
                        if not tmp:
                            continue
                        item3 = tmp.get(o_apMac, {})
                        if not item3:
                            continue
                    except:
                        traceback.print_exc()
                    c_rssi = item3['rssi']
                    c_channel = item3['channel']
                    if o_channel == c_channel and c_rssi != -100:
                        train_X.append(o_rssi)
                        train_Y.append(c_rssi)
        length = len(train_Y)
        train_X = np.array(train_X).reshape((length, 1))
        regr = linear_model.LinearRegression()
        newParameterDict = {'a': 0, 'b': 0}
        if len(train_X) != 0 and len(train_Y) != 0:
            regr.fit(train_X, train_Y)
            a = regr.coef_
            b = regr.intercept_
            newParameterDict['a'] = a
            newParameterDict['b'] = b
        return newParameterDict

    # 计算信号强度分布占比Q
    def computeQ(self, trainDataList):
        Q = 0
        if len(trainDataList) != 0:
            s_rssi_range = set()
            s_location_range = set()
            for item in trainDataList:
                fingerDataList = item.getFingerDataList()
                s_location_range.add(item.locationID)
                for item2 in fingerDataList:
                    rssi = item2.rssi
                    s_rssi_range.add(rssi)
            fd_dict = InitialFDLoader.getInitialFD()
            location_times = 0
            for location in s_location_range:
                if location in fd_dict.keys():
                    location_times += 1
            ratio_rssi = len(s_rssi_range) / 60
            ratio_location = location_times / len(fd_dict.keys())
            # Q = round(ratio_rssi * ratio_location, 2)
            Q = round(ratio_rssi, 2)
        return Q
