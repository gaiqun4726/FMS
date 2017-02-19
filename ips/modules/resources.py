# coding=utf-8
import Queue


# 所有全局共享的队列、指纹库字典都放在这个文件里

# 全局共享的缓冲队列
class QueueResources(object):
    bufferQueue = Queue.Queue()
    wifiMessageQueue = Queue.Queue()
    locatingMessageQueue = Queue.Queue()


# 全局共享的指纹库字典
class DictResources(object):
    spectrumDict = {}
