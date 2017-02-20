# coding=utf-8

import threading
from threading import Timer
import stomp
from resources import QueueResources

bufferQueue = QueueResources.bufferQueue
wifiMessageQueue = QueueResources.wifiMessageQueue
lock = threading.Lock()  # 缓冲队列锁


# 从Activemq提取Wi-Fi探针数据的线程类
class Receiver(threading.Thread):
    class ActivemqListener(object):
        def on_message(self, header, msg):
            global bufferQueue
            bufferQueue.put(msg)
            # print msg

    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)

    def run(self):
        # 使用stomp协议从默认端口（61616）的消息队列中提取探针数据，并写入bufferQueue
        conn = stomp.Connection10()
        conn.set_listener('', Receiver.ActivemqListener())
        conn.start()
        conn.connect()
        conn.subscribe('aruba')
        conn.disconnect()


# 从bufferQueue中抽取定位所需的实时数据包线程类
class Collector(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)
        self.wifiMessageList = []
        self.cycle = 2  # 采样周期

    def setBlockMessage(self, msg):
        global wifiMessageQueue
        wifiMessageQueue.put(self.wifiMessageList)
        self.wifiMessageList = []

    # 将采样周期之内的数据包封装到一起，发送给wifiMessageQueue缓冲队列
    def getBlockMessage(self, msg):
        global lock
        lock.acquire()
        while bufferQueue.empty() is False:
            self.wifiMessageList.append(bufferQueue.get())
        lock.release()
        self.setBlockMessage(0)
        Timer(self.cycle, self.getBlockMessage, (0,)).start()

    def run(self):
        Timer(self.cycle, self.getBlockMessage, (0,)).start()
