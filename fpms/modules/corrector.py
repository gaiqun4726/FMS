# coding=utf-8

# from loader import InitialFDLoader, PartialFDLoader, ParameterLoader
from extractor import TagedSRCData

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
        self.parameterList = []
        self.tagedSRCDataList = tagedSRCDataList
        self.updateDataList = []

    # 将更新数据校正后，返回更新数据列表
    def getUpdateDataList(self):
        rp = RegeressionPar(self.muMac, self.tagedSRCDataList)
        self.parameterUsability = rp.hasParameter()
        if self.parameterUsability is True:
            self.parameterList = rp.getParameter()
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
        self.initialFD = {}
        self.parameterList = []
        self.trainDataList = []
        self.Q = 0
        self.parameterUsability = False
        self.autoUpdate()

    # 是否已经可以使用回归系数
    def hasParameter(self):
        return self.parameterUsability

    # 返回回归系数
    def getParameter(self):
        return self.parameterList

    # 自动判断回归系数表是否需要更新
    def autoUpdate(self):
        self.loadDataBaseData()
        self.setDataBaseData()

    # 从数据库读取回归系数表记录
    def loadDataBaseData(self):
        self.Q = 0
        self.parameterList = []
        self.trainDataList = []

    # 重新设置回归系数表，主要是添加训练数据或清空训练数据
    def setDataBaseData(self):
        # 如果满足产生计算的条件，本次计算也不更改内存中的系数，在下一次读取时再改变系数
        self.trainDataList.append(self.tagedSRCDataList)
        # 计算Q的业务逻辑
        if self.Q < standardQ:
            # 将原来的系数、Q和训练数据存入数据库
            pass
        else:
            newParameterList = self.computeParameter()
            # 将Q和训练数据清空
            self.Q = 0
            self.trainDataList = []
            # 将新的系数、Q、训练数据存入数据库
            self.parameterUsability = True
            pass

    # 使用训练数据构建线性回归方程，并求解回归方程的回归系数
    def computeParameter(self):
        newParameterList = []
        return newParameterList
