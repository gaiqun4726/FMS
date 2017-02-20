# coding=utf-8
import numpy as np
from pandas import DataFrame

# from loader import InitialFDLoader, PartialFDLoader
from sklearn.cluster import AffinityPropagation

spectrumDict = {}


class Calculator(object):
    def __init__(self):
        # self.initialFD = InitialFDLoader.getInitialFD()
        # self.partialFD = PartialFDLoader.getPartialFD()
        self.initialFD = {}
        self.partialFD = {}
        self.updateFD = {}

    def calculate(self):
        sc = SpaceCluster()
        clusterToLocationDict, LocationToClusterDict = sc.getClusterResults()

    def predict(self):
        predictList = list(combinations(self.locationList, int(self.amount)))
        for item in predictList:
            df_train = DataFrame(self.trainDict)
            df1 = df_train.ix[:, item]
            X1 = df1.applymap(lambda x: x[0]).values
            df_predict = DataFrame(self.predictDict)
            df2 = df_predict.ix[:, item]
            X2 = df2.applymap(lambda x: x[0]).values
            remainList = list(set(self.locationList) - set(item))
            for locationY in remainList:
                df1_y = df_train.ix[:, locationY]
                Y1 = df1_y.values
                Y1 = [y1[0] for y1 in Y1]
                df2_y = df_predict.ix[:, locationY]
                Y2 = df2_y.values
                Y2 = [y2[0] for y2 in Y2]
                pls = PLSRegression()
                pls.fit(X1, Y1)
                Y2_predict = pls.predict(X2)
                diff = []
                for x in range(len(Y2)):
                    diff.append(round(abs(Y2_predict[x] - Y2[x])))
                self.diffList.extend(diff)


class SpaceCluster(object):
    def __init__(self):
        self.X = 0
        self.labels = 0
        self.locationToClusterDict = {}
        self.clusterToLocationDict = {}

    def getFDArray(self):
        df = DataFrame(spectrumDict).T
        self.X = df.applymap(lambda x: x[0]).values
        self.labels = list(df.index)

    def cluster(self):
        af = AffinityPropagation().fit(self.X)
        cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_
        n_clusters_ = len(cluster_centers_indices)
        for seq in range(len(labels)):
            cls = labels[seq]
            locationList = self.clusterToLocationDict.get(cls, [])
            locationList.append(self.labels[seq])
            self.clusterToLocationDict[cls] = locationList
            self.locationToClusterDict[self.labels[seq]] = cls
    
    def getClusterResults(self):
        self.getFDArray()
        self.cluster()
        return self.locationToClusterDict, self.clusterToLocationDict


# if __name__ == '__main__':
#     sp = SpectrumLoader()
#     sp.loadSpectrum()
#     sc = SpaceCluster()
#     sc.getFDArray()
