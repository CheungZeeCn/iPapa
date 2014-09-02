#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-01-26 16:47:37 
# Copyright 2014 NONE rights reserved.

import threading
import logging
import time
import Queue
from iFetcher import Fetcher
import util
import os
from setup import iPapa

myLogger = None
if 'iPapa_worker' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_worker')


class Worker(threading.Thread):
    def __init__(self, myId, myManager):
        threading.Thread.__init__(self, name=myId)
        self.m = myManager
        self.inQueue = myManager.inQueue
        self.outQueue = myManager.outQueue
        self.hungerly = False
        self.daemon = True
        self.timeStampBegin = time.time()
        myLogger.debug("my manager's inQueue size [%d]" % (self.inQueue.qsize()))
        self.fetcher = Fetcher()

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
                    if self.m.shouldExit == True:
                        myLogger.debug('thread [%s] is exiting' % (self.name))
                        break
                if self.hungerly == False:
                    # do
                    myLogger.info("thread [%s], get task[%s] from queue" % (self.name, get.id))
                    time.sleep(3)
                    # put
                    self.doOneTask(get)
                else:
                    time.sleep(2)
            except Exception, e:
                util.printException()
                myLogger.error('sth wrong[%s] in thread [%s]' % (e, self.name))
                get.status =  'failed'
                if get.msg !=  '':
                    get.msg = util.exprException()
                #break
        myLogger.debug('thread [%s] exit!' % (self.name))

    def signTask(self, task):
        task.handleBy = "w_%s" % self.name
        task.signTs.append((task.handleBy, time.time()))

    def doOneTask(self, task):
        """
        """
        self.signTask(task)
        task.status = 'down'
        outData = None
        if task.taskType == 'page': 
            data = self.fetcher.keepFetchRead(task.url, task.postdata, task.timeout, task.tryTimes, True)
        elif task.taskType == 'media':
            #genPath
            to = ''
            if task.dest != '':
                to = task.dest
            else:
                # todo mk it more random
                to = util.getUrlFileName(task.url)
                if to == '':
                    to = "unameFile"
                task.dest = to
            dirPath = iPapa.iTsOutputPath
            to = os.path.join(dirPath, to)
            data = self.fetcher.download(task.url, to, task.postdata, task.timeout, task.tryTimes, True)

        if data == None: #download error
            # set sth, put it into error     
            task.status = 'failed'
            task.msg = 'download failed'
            myLogger.error('[wThread_%s]Fetcher data failed in task.id[%d]' % (self.name, task.id))
        else: # OK
            task['__data'] = data
            task.status = 'downed'

        self.outQueue.put(task) 


if __name__ == '__main__':
    print 'hello world'

