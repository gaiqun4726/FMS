# coding=utf-8
import pandas as pd
from resources import DictResources
from pandas import DataFrame
import numpy as np
from sklearn.cluster import AffinityPropagation

spectrumDict = DictResources.spectrumDict


# 将指纹库读入内存的指纹库字典
class SpectrumLoader(object):
    def __init__(self,
                 fp_path=r"L:\Graduation Project\finger data\middleFile\2017-01-20\B4-0B-44-2F-C8-A2spectrum.csv"):
        self.path = fp_path

    # 从指纹库的csv文件加载指纹库字典
    def loadSpectrum(self):
        df = pd.read_csv(self.path, index_col='locationID')
        global spectrumDict
        for key1 in df.index:
            sr = df.ix[key1]
            lv2val = {}
            for key2 in sr.index:
                lv2val[key2] = [sr[key2], ]
            spectrumDict[key1] = lv2val

        print 'load spectrum finished'

    # 从数据库加载指纹库字典
    def loadSpectrumFromDB(self):
        pass


class SpaceCluster(object):
    def __init__(self):
        self.X = 0
        self.labels = 0

    def getFDArray(self):
        df = DataFrame(spectrumDict).T
        self.X = df.applymap(lambda x: x[0]).values
        self.labels = list(df.index)
        # print df.applymap(lambda x: x[0]).values

    def cluster(self):
        af = AffinityPropagation().fit(self.X)
        cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_
        n_clusters_ = len(cluster_centers_indices)
        res_dict = {}
        for seq in range(len(labels)):
            cls = labels[seq]
            locationList = res_dict.get(cls, [])
            locationList.append(self.labels[seq])
            res_dict[cls] = locationList
        print res_dict


if __name__ == '__main__':
    sl = SpectrumLoader()
    sl.loadSpectrum()
    sc = SpaceCluster()
    sc.getFDArray()
    sc.cluster()
