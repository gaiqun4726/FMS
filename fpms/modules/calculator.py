# coding=utf-8
import numpy as np
from pandas import DataFrame

# from loader import InitialFDLoader, PartialFDLoader

spectrumDict = {}


class Calculator(object):
    def __init__(self):
        pass
        # self.initialFD = InitialFDLoader.getInitialFD()
        # self.partialFD = PartialFDLoader.getPartialFD()

    def calculate(self):
        pass


class SpaceCluster(object):
    def getFDArray(self):
        df = DataFrame(spectrumDict)
        print np.array(df)


if __name__ == '__main__':
    sp = SpectrumLoader()
    sp.loadSpectrum()
    sc = SpaceCluster()
    sc.getFDArray()
