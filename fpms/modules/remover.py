# coding=utf-8
# from loader import InitialFDLoader, PartialFDLoader, ParameterLoader
from extractor import TagedSRCData

standard_Q = .3


class Remover(object):
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
    def __init__(self, mu_mac, tagedSRCDataList):
        self.mu_mac = mu_mac
        self.has_parameter = False
        self.parameterList = []
        self.tagedSRCDataList = tagedSRCDataList
        self.updateDataList = []

    def getUpdateDataList(self):
        rp = RegeressionPar(self.mu_mac, self.tagedSRCDataList)
        self.has_parameter = rp.hasParameter()
        if self.has_parameter is True:
            self.parameterList = rp.getParameter()
            for tagedSRCData in self.tagedSRCDataList:
                updateData = self.removeDiff()
                self.updateDataList.append(updateData)

        return self.updateDataList

    def removeDiff(self):
        fingerDataList = []
        updateData = TagedSRCData(self.mu_mac)
        updateData.setFingerDataList(fingerDataList)
        return updateData


class RegeressionPar(object):
    global standard_Q

    def __init__(self, mu_mac, tagedSRCDataList):
        self.mu_mac = mu_mac
        self.tagedSRCDataList = tagedSRCDataList
        self.initialFD = {}
        self.parameterList = []
        self.trainDataList = []
        self.Q = 0
        self.has_parameter = False
        self.autoUpdate()

    def hasParameter(self):
        return self.has_parameter

    def getParameter(self):
        return self.parameterList

    def autoUpdate(self):
        self.loadDataBaseData()
        self.setDataBaseData()

    def loadDataBaseData(self):
        self.Q = 0
        self.parameterList = []
        self.trainDataList = []

    def setDataBaseData(self):
        # 如果满足产生计算的条件，本次计算也不更改内存中的系数，在下一次读取时再改变系数
        self.trainDataList.append(self.tagedSRCDataList)
        # 计算Q的业务逻辑
        if self.Q < standard_Q:
            # 将原来的系数、Q和训练数据存入数据库
            pass
        else:
            newParameterList = self.computeParameter()
            # 将Q和训练数据清空
            self.Q = 0
            self.trainDataList = []
            # 将新的系数、Q、训练数据存入数据库
            self.has_parameter = True
            pass

    def computeParameter(self):
        newParameterList = []
        return newParameterList
