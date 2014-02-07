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
from zlFetcher import zlFetcher

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
        self.fetcher = zlFetcher()

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
                    myLogger.info("thread [%s], get [%s] from queue" % (self.name, get))
                    time.sleep(3)
                    # put
                    self.doOneTask(get)
                else:
                    time.sleep(2)
            except Exception, e:
                myLogger.error('sth wrong[%s] in thread [%s]' % (e, self.name))
                break
        myLogger.debug('thread [%s] exit!' % (self.name))

    def doOneTask(self, task):
        """
        task structure: #unicode encoded
            {
                'id': id,  #assigned by input file or manager
                'inData': inData, # input, can be any type 
                'outData': outData, # output, can be any type
                'status': status, #'OK', 'ERROR', 'None'
                'msg': 'default' 
            } 
        """
        outData = []
        kw = task['inData'] # task['inData'] should be in unicode
        n = self.fetcher.getKwN(kw)
        myLogger.debug("getKwN kw[%s] n[%s]" % (kw, n))
        if n < 0: # maybe error or not thing
            #outData = []
            task['status'] = 'ERROR'
            task['msg'] = 'ERROR occured in retrieveling patents for this kw'
            myLogger.error("getKwN kw[%s] n[%s], check it" % (kw, n))
        elif n == 0:
            task['status'] = 'NONE'
            task['msg'] = 'NO patent for this kw'
            myLogger.warn("getKwN kw[%s] n[%s], so sad" % (kw, n))
        else: 
            ret =  self.fetcher.getKwNUrl(kw, n)
            myLogger.debug("all kw[%s] patent url got[%s]" % (task['inData'], len(ret)))
            isAllOk = True

            for each in ret:
                #print "%s\t%s\t%s" % (tuple(each))
                try:
                    detail = self.fetcher.getPatentDetail(each[2])
                    #print "%s" % (detail)
                    outData.append(detail)
                except Exception, e:
                    isAllOk = False
                    myLogger.error("failed in fetching %s_%s_%s_[%s], %s" % \
                                        (kw, each[0], each[1], each[2], e))

            if isAllOk == False:
                task['msg'] = 'Done, but some patent could not be retrieval'
            else:     
                task['msg'] = 'Done'
            task['status'] = 'OK'

        task['outData'] = outData
        self.outQueue.put(task) 


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

