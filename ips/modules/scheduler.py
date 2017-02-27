# coding=utf-8
import Queue
from collector import Receiver, Collector
from preprocessor import Preprocessor
from locator import Locator
from loader import SpectrumLoader


# IPS的启动器，启动数据采集、预处理、指纹库加载、定位等线程
class Scheduler(object):
    bufferQueue = Queue.Queue()  # 从Activemq接收Wi-Fi探针数据的缓冲队列

    @staticmethod
    def startIPS():
        receiverThread = Receiver('receiver')
        collectorThread = Collector('collector')
        preprocessorThread = Preprocessor('preprocessor')

        receiverThread.start()
        collectorThread.start()
        preprocessorThread.start()

        spectrumLoader = SpectrumLoader()
        spectrumLoader.loadSpectrum()

        locatingThread = Locator('locating')
        locatingThread.start()


# 仅限于本地测试，在web服务器部署时用不到
if __name__ == '__main__':
    Scheduler.startIPS()
