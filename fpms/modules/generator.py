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


class Generator(threading.Thread):
    def __init__(self, threadName, dateTime):
        threading.Thread.__init__(self, name=threadName)
        self.dateTime = dateTime

    def run(self):
        self.update()

    def update(self):
        print(u'------指纹库自动更新维护start------')
        preProcessor = PreProcessor(self.dateTime)
        if not preProcessor.checkInitialFD():
            print(u'创建初始指纹库start')
            initialFDGenerator = InitialFDGenerator()
            initialFDGenerator.mergeFiles()
            initialFDGenerator.generateFD()
            print(u'创建初始指纹库end')
        print(u'探针数据按MAC地址分类start')
        preProcessor.mergeFiles()
        print(u'探针数据按MAC地址分类end')
        muSet = preProcessor.allMuSet
        print(u'------全天指纹库更新数据处理start------')
        count = 0
        for muMac in muSet:
            print(u'处理mu为%s' % muMac)
            print(u'预处理start')
            collectWifiData = preProcessor.loadData(muMac)
            print(u'预处理end')
            print(u'更新数据提取start')
            extractor = Extractor(muMac, collectWifiData[0], collectWifiData[1])
            tagedSRCDataList = extractor.getTagedSRCDataList()
            # if tagedSRCDataList:
            #     print 'yes'
            print(u'更新数据提取end')
            print(u'设备信号差异校正start')
            corrector = Corrector(muMac, tagedSRCDataList)
            updateDataList = corrector.getUpdateDataList()
            print(u'设备信号差异校正end')
            if updateDataList != []:
                count += 1
                print(u'部分更新指纹库更新start')
                mergeData = MergeData()
                mergeData.mergeDataToPartialFD(updateDataList)
                print(u'部分更新指纹库更新end')
            print(u'%s处理完毕' % muMac)
        print(u'------全天指纹库更新数据处理end------')
        print(u'------更新数据库生成start------')
        calculator = Calculator('', self.dateTime)
        calculator.calculate()
        print(u'------更新数据库生成end------')
        print(u'------指纹库自动更新维护end------')
        path = ResLoader.getStatisticsResultsPath()
        fh = open(os.path.join(path, datetime + '.txt'), 'w')
        fh.write(u'全天MU数量'.encode('utf') + ':' + str(len(muSet)) + '\n')
        fh.write(u'更新数据数量'.encode('utf') + ':' + str(count) + '\n')
        fh.close()
