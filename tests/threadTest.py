# coding=utf-8
import threading
from threading import Timer
import time

count = 0


# def loopfunc(msg, starttime):
#     global count
#     print u'启动时刻：', starttime, ' 当前时刻：', time.time(), '消息 --> %s' % (msg)
#     Timer(3, loopfunc, ('world %d' % (count), time.time())).start()
#
# Timer(3, loopfunc, ('world %d' % (count), time.time())).start()

class T1(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)
        self.threadName = threadName

    def run(self):
        for i in range(40):
            print(self.threadName + '--%d\n' % i)


class T2(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)

    def run(self):
        for i in range(40):
            print('T2:%d\n' % i)


for i in range(3):
    t = T1('t%d' % i)
    t.start()
    t.join()
