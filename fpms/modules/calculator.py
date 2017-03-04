# coding=utf-8

import numpy as np
from pandas import DataFrame
from sklearn.cluster import AffinityPropagation
from sklearn.cross_decomposition import PLSRegression
import pickle
import os
import math

from loader import InitialFDLoader, PartialFDLoader, ResLoader, ClusterResultsLoader
from fpms.models import PartialFD


# 使用部分更新指纹库中的数据对缺失指纹进行推算，从而构建完整更新指纹库的类
class Calculator(object):
    def __init__(self):
        self.initialFD = InitialFDLoader.getInitialFD()
        self.partialFD = PartialFDLoader().getPartialFD()
        self.updateFD = {}

    # 将部分更新指纹库中的历史数据进行融合
    def mergeHistory(self, locationID, apMac):
        historyDataPath = os.path.join(ResLoader.getPartialFDHistoryDataPath(),
                                       self.partialFD[locationID][apMac]['historyDataPath'])
        channel = self.initialFD[locationID][apMac]['channel']
        historyDataList = []
        with open(historyDataPath, "rb") as historyDataFile:
            try:
                while True:
                    historyData = pickle.load(historyDataFile)
                    history_channel = historyData.channel
                    if history_channel == channel:
                        historyDataList.append(historyData.rssi)
            except EOFError:
                pass
        meanRssi = round(np.mean(historyDataList))
        self.partialFD[locationID][apMac]['rssi'] = meanRssi
        self.partialFD[locationID][apMac]['channel'] = channel
        # 融合数据后，将部分更新指纹库和历史记录都清空
        historyDataFile = open(historyDataPath, "wb")
        historyDataFile.truncate()
        historyDataFile.close()
        record = PartialFD.objects.filter(locationID=locationID, apMAC=apMac)
        record.delete()

    def checkUpdatability(self, cls):
        clusterToLocationDict, locationToClusterDict = ClusterResultsLoader.getClusterResults()
        locationList = clusterToLocationDict[cls]
        count = 0
        for locationID in locationList:
            partialFDRes = self.partialFD[locationID]
            initialFDRes = self.initialFD[locationID]
            if len(partialFDRes.keys()) == len(initialFDRes.keys()):
                count += 1
        return count > math.floor(len(locationList) / 2)

        # 使用偏最小二乘回归对缺失指纹进行推算

    def calculate(self, dict1, dict2):
        # 将部分更新指纹库中数据求均值，将缺失指纹进行推算，并写入更新指纹库
        pass

    def predict(self, predictLocation, trainLocationList):
        pass


    # 评价推测指纹的准确性
    # def predict(self):
    #     predictList = list(combinations(self.locationList, int(self.amount)))
    #     for item in predictList:
    #         dfTrain = DataFrame(self.trainDict)
    #         df1 = dfTrain.ix[:, item]
    #         X1 = df1.applymap(lambda x: x[0]).values
    #         dfPredict = DataFrame(self.predictDict)
    #         df2 = dfPredict.ix[:, item]
    #         X2 = df2.applymap(lambda x: x[0]).values
    #         remainList = list(set(self.locationList) - set(item))
    #         for locationY in remainList:
    #             df1_y = dfTrain.ix[:, locationY]
    #             Y1 = df1_y.values
    #             Y1 = [y1[0] for y1 in Y1]
    #             df2_y = dfPredict.ix[:, locationY]
    #             Y2 = df2_y.values
    #             Y2 = [y2[0] for y2 in Y2]
    #             pls = PLSRegression()
    #             pls.fit(X1, Y1)
    #             Y2_predict = pls.predict(X2)
    #             diff = []
    #             for x in range(len(Y2)):
    #                 diff.append(round(abs(Y2_predict[x] - Y2[x])))
    #             self.diffList.extend(diff)


# 使用吸引子传播算法对参考点进行空间聚类
class SpaceCluster(object):
    def __init__(self):
        self.X = 0
        self.labels = []
        self.locationToClusterDict = {}
        self.clusterToLocationDict = {}

    # 将dict类型的指纹转化成array
    def getFDArray(self):
        fd_dict = InitialFDLoader.getInitialFD()
        df = DataFrame(fd_dict).T
        self.X = df.applymap(lambda x: x[0]).values
        self.labels = list(df.index)

    # 吸引子传播聚类方法
    def cluster(self):
        af = AffinityPropagation().fit(self.X)
        clusterCenterIndices = af.cluster_centers_indices_
        labels = af.labels_
        n_clusters_ = len(clusterCenterIndices)
        for seq in range(len(labels)):
            cls = labels[seq]
            locationList = self.clusterToLocationDict.get(cls, [])
            locationList.append(self.labels[seq])
            self.clusterToLocationDict[cls] = locationList
            self.locationToClusterDict[self.labels[seq]] = cls

    # 得到聚类结果的字典，一个是类别中的所有参考点，一个事参考点所属的类别
    def getClusterResults(self):
        self.getFDArray()
        self.cluster()
        return self.locationToClusterDict, self.clusterToLocationDict

# if __name__ == '__main__':
#     sp = SpectrumLoader()
#     sp.loadSpectrum()
#     sc = SpaceCluster()
#     sc.getFDArray()
