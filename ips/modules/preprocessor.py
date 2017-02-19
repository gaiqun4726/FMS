# coding=utf-8
import Queue
import threading
from scipy.stats import mode
from resources import QueueResources
import math

wifiMessageQueue = QueueResources.wifiMessageQueue
locatingMessageQueue = QueueResources.locatingMessageQueue


# 预处理类
class Preprocessor(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)
        self.locatingMessageDict = {}

    # 从消息队列中提取采样周期内的数据包
    def getMessage(self):
        global wifiMessageQueue
        block = wifiMessageQueue.get()
        # print block
        self.preprocess(block)
        locatingMessageQueue.put(self.locatingMessageDict)
        # print self.locatingMessageDict
        self.locatingMessageDict = {}

    # 预处理，将数据包按照muMac和apMac建立实时信号字典
    def preprocess(self, block):
        muMessageDict = {}
        for item in block:
            messageList = self.parseMessage(item)
            if messageList != -1:
                muMac = messageList[0]
                apMac = messageList[1]
                muApMessageDict = muMessageDict.get(muMac, {})
                muApMessageList = muApMessageDict.get(apMac, [])
                muApMessageList.append(messageList[2:])
                muApMessageDict[apMac] = muApMessageList
                muMessageDict[muMac] = muApMessageDict
        for mu in muMessageDict.keys():
            messageDict = muMessageDict[mu]
            for ap in messageDict.keys():
                messageList = messageDict[ap]
                bestChannel = self.getBestChannel(messageList)
                rssi = self.dataPick(messageList, bestChannel)
                lv1val = self.locatingMessageDict.get(mu, {})
                lv1val[ap] = [rssi, bestChannel]
                self.locatingMessageDict[mu] = lv1val

    # 选取采样周期内的最佳信道
    def getBestChannel(self, messageList):
        channelList = []
        for message in messageList:
            channelList.append(int(message[1]))
        res = mode(channelList)
        return res[0][0]

    # 使用最佳信道的数据，求均值
    def dataPick(self, messageList, bestChannel):
        rssiList = []
        for message in messageList:
            if int(message[1]) == bestChannel:
                rssiList.append(int(message[0]))
        return round(sum(rssiList) / len(rssiList))

    # 从数据包的报文中解析wifi数据字符串
    def parseMessage(self, message):
        items = message.split(',')
        if len(items) != 11:
            return -1
        return [items[2], items[1], items[3], items[4]]

    def run(self):
        while True:
            self.getMessage()
