# coding=utf-8
from extractor import *
from preprocessor import *


class Scheduler(object):
    def invoker(self):
        while True:
            preprocessor = PreProcessor('a',2017)
            processed_df = preprocessor.kalmanFilter(preprocessor.filterData(preprocessor.loadData()))
            extractor = Extractor()

            if self.checkPartialFD() is True:
                pass

    def checkPartialFD(self):
        return True