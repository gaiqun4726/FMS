# coding=utf-8
import numpy as np
from pandas import DataFrame

# from loader import InitialFDLoader, PartialFDLoader
from sklearn.cluster import AffinityPropagation

spectrumDict = {}


# 使用部分更新指纹库中的数据对缺失指纹进行推算，从而构建完整更新指纹库的类
class Calculator(object):
    def __init__(self):
        # self.initialFD = InitialFDLoader.getInitialFD()
        # self.partialFD = PartialFDLoader.getPartialFD()
        self.initialFD = {}
        self.partialFD = {}
        self.updateFD = {}

    # 使用偏最小二乘回归对缺失指纹进行推算
    def calculate(self, dict1, dict2):
        # 将部分更新指纹库中数据求均值，将缺失指纹进行推算，并写入更新指纹库
        pass

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
        df = DataFrame(spectrumDict).T
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
