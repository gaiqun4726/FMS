# coding=utf-8

from threading import Timer
import threading
from datetime import datetime, timedelta

from preprocessor import *
from extractor import *
from corrector import *
from calculator import *
from loader import ResLoader

strFormat = "%Y-%m-%d"
refPointsRate = .5
updateCycle = 24 * 60 * 60


# 定期执行指纹库更新程序的线程类
class Scheduler(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)

    def run(self):
        self.generateUpdateFD(0)

    # 定期更新指纹库
    def generateUpdateFD(self, msg):
        print('------指纹库更新操作start------')
        yesterday = datetime.now() - timedelta(days=1)
        dateTime = datetime.strftime(yesterday, strFormat)
        print('------探针数据按MAC地址分类start------')
        preprocessor = PreProcessor(dateTime)
        if preprocessor.checkInitialFD() is False:
            print('指纹库未更新！')
            return
        preprocessor.mergeFiles()
        print('------探针数据按MAC地址分类end------')
        muSet = preprocessor.allMuSet
        print('------全天指纹库更新数据提取start------')
        for muMac in muSet:
            print('处理mu为%s' % muMac)
            collectWifiData = preprocessor.loadData(muMac)
            extractor = Extractor(collectWifiData)
            tagedSRCDataList = extractor.getTagedSRCDataList()
            remover = Remover(tagedSRCDataList)
            updateDataList = remover.getUpdateDataList()
            mergeData = MergeData()
            mergeData.mergeDataToPartialFD(updateDataList)
            print('处理完毕')
        print('------全天指纹库更新数据提取end------')

        partialFD = {}
        spaceCluster = SpaceCluster()
        dict1, dict2 = spaceCluster.getClusterResults()
        if self.checkPartialFD(partialFD, dict1, dict2) is True:
            calculator = Calculator()
            calculator.calculate(dict1, dict2)
            print('指纹库更新成功!')
        else:
            print('更新数据不够，今日暂不更新指纹库!')
        print('------指纹库更新操作end------')
        Timer(updateCycle, self.generateUpdateFD, (0,)).start()

    # 检查部分更新指纹库是否已经满足指纹库更新条件
    def checkPartialFD(self, partialFD, dict1, dict2):
        # 检查部分更新指纹库中，是否每个聚类分区中都有超过30%的更新数据
        return True
