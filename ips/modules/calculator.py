# coding=utf-8
from loader import *
from itertools import combinations
import matplotlib.pyplot as plt
from pandas import DataFrame
from sklearn.cross_decomposition import PLSRegression
from pylab import *


class FpCalculator(object):
    def __init__(self, path1, path2):
        self.locationList = [30026016, 30030016, 30034019, 30038023, 30046023, 30054023, 30034013, 30034010, 30034007,
                             30038013]
        self.quota = .4
        self.amount = round(len(self.locationList) * self.quota)
        self.trainDict = {}
        self.predictDict = {}
        self.path1 = path1
        self.path2 = path2
        self.diffList = []

    def loadSpectrum(self):
        df = pd.read_csv(self.path1, index_col='locationID')
        for key1 in df.index:
            sr = df.ix[key1]
            lv2val = {}
            for key2 in sr.index:
                lv2val[key2] = [sr[key2], ]
            self.trainDict[key1] = lv2val
        df2 = pd.read_csv(self.path2, index_col='locationID')
        for key1 in df2.index:
            sr = df2.ix[key1]
            lv2val = {}
            for key2 in sr.index:
                lv2val[key2] = [sr[key2], ]
            self.predictDict[key1] = lv2val
            # print self.trainDict, '\n', self.predictDict

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

        # print self.diffList

    def show(self):
        self.diffList.sort()
        amount_dict = {}
        for x in self.diffList:
            amount = amount_dict.get(x, 0)
            amount += 1
            amount_dict[x] = amount
        Y = []
        keys = amount_dict.keys()
        keys.sort()
        for x in keys:
            Y.append(amount_dict[x])
        sumy = sum(Y)
        Y = [float(y) / float(sumy) for y in Y]
        CY = np.cumsum(Y)

        mpl.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.set_title(u'推测信号强度偏差累计概率分布图')
        ax1.plot(keys, CY, 'r--')
        plt.show()


if __name__ == '__main__':
    path1 = r"L:\Graduation Project\finger data\middleFile\2017-01-20\B4-0B-44-2F-C8-A2spectrum.csv"
    path2 = r"J:\demo\2017-02-17\B4-0B-44-2F-C8-A2spectrum.csv"
    fp = FpCalculator(path1, path2)
    fp.loadSpectrum()
    fp.predict()
    fp.show()
