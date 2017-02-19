# coding=utf-8
import threading
from threading import Timer
import time

count = 0


def loopfunc(msg, starttime):
    global count
    print u'启动时刻：', starttime, ' 当前时刻：', time.time(), '消息 --> %s' % (msg)
    Timer(3, loopfunc, ('world %d' % (count), time.time())).start()

Timer(3, loopfunc, ('world %d' % (count), time.time())).start()
