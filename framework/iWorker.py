#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-01-26 16:47:37 
# Copyright 2014 NONE rights reserved.

import threading
import logging
import time
import Queue
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler 
import HttpWatcher

myLogger = None
if 'iPapa_worker' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_worker')


class Worker(threading.Thread):
    def __init__(self, myId, myManager):
        threading.Thread.__init__(self, name=myId)
        self.inQueue = myManager.inQueue
        self.outQueue = myManager.outQueue
        self.hungerly = False
        self.daemon = True
        self.timeStampBegin = time.time()
        myLogger.debug("my manager's inQueue size [%d]" % (self.inQueue.qsize()))

    def isHungerly(self):
        return self.hungerly

    def run(self):
        myLogger.info("worker %s begin to run" % (self.name))
        myLogger.info("my manager's inQueue size [%d]" % (self.inQueue.qsize()))
        self.hungerly = False
        while True:
            try:
                # get 
                get = None
                try:
                    get = self.inQueue.get(timeout=1)
                    self.hungerly = False
                except Queue.Empty, e:
                    self.hungerly = True
                    myLogger.debug('thread [%s] is hungerly now' % (self.name))

                if self.hungerly == False:
                    # do
                    myLogger.info("thread [%s], get [%s] from queue" % (self.name, get))
                    time.sleep(3)
                    # put
                    put = "thread [%s], get [%s] from queue, Done" % (self.name, get)
                    self.outQueue.put(put)
                    pass
                else:
                    time.sleep(2)
            except Exception, e:
                myLogger.error('sth wrong[%s] in thread [%s]' % (e, self.name))
                break

class Controller(threading.Thread):
    def __init__(self, myManager):
        threading.Thread.__init__(self, name='controller')
        self.m = myManager
        self.timeStampBegin = time.time()
        self.daemon = True
    
    def isAllDone(self):
        return self.myManager.isAllDone()

    def run(self):
        HttpWatcher.run(port=28282, m=self.m)


if __name__ == '__main__':
    print 'hello world'

