#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 20:03:10 
# Copyright 2014 NONE rights reserved.

import threading
import logging
import time
import Queue
import sys
import util
import os
from setup import iPapa

myLogger = None
if 'iPapa_parser' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_parser')

class Parser(threading.Thread):
    def __init__(self, myId, myManager):
        threading.Thread.__init__(self, name=myId)
        self.m = myManager
        self.inPQueue = myManager.inPQueue
        self.outPQueue = myManager.outPQueue
        self.hungerly = False
        self.daemon = True
        self.timeStampBegin = time.time()
        myLogger.debug("my manager's inPQueue size [%d]" % (self.inPQueue.qsize()))
        self.hs = {}

    def isHungerly(self):
        return self.hungerly

    def run(self):
        myLogger.info("parser %s begin to run" % (self.name))
        myLogger.info("my manager's inPQueue size [%d]" % (self.inPQueue.qsize()))
        self.hungerly = False
        while True:
            try:
                # get 
                get = None
                try:
                    get = self.inPQueue.get(timeout=1)
                    self.hungerly = False
                except Queue.Empty, e:
                    self.hungerly = True
                    myLogger.debug('pThread [%s] is hungerly now' % (self.name))
                    # mama call me home
                    if self.m.shouldExit == True:
                        myLogger.debug('pThread [%s] is exiting' % (self.name))
                        break

                if self.hungerly == False:
                    myLogger.info("thread [%s], get stask.id[%s] from queue" % (self.name, get.id))
                    # put
                    if get.status == 'failed':
                        self.outPQueue.put(get)
                        myLogger.error("thread [%s], put failed task.id[%s] into PQueue" % (self.name, get.id))
                    else:    
                        self.doOneTask(get)
                else:
                    time.sleep(2)
            except Exception, e:
                util.printException()
                myLogger.error('sth wrong[%s] in pThread [%s]' % (e, self.name))
                task.status =  'failed'
                if task.msg !=  '':
                    task.msg = util.exprException()
                #break
        myLogger.debug('pThread [%s] exit!' % (self.name))

    def signTask(self, task):
        task.handleBy = "p_%s" % self.name
        task.signTs.append((task.handleBy, time.time()))

    def doOneTask(self, task):
        #0. sign it 
        self.signTask(task)     
        task.status = 'parsing'
        #1. call handler 
        if task.handler not in self.hs: 
            #from MainPageHandler import MainPageHandler
            m = __import__(task.handler)
            c = getattr(m, task.handler)
            self.hs[task.handler] = c()
        h = self.hs[task.handler]

        #2. check type and do it
        isOK = True
        if task.taskType in ('media', 'page'): 
            #deal with it
            output = {}
            try:
                output = h.parse(task)
            except Exception, e:
                # todo  set task failed here 
                util.printException()
                myLogger.error("sth wrong [%s][%s] in parsing, set task[%d] failed" % (task.handler, e, task.id))
                isOK = False
            if 'newTasks' in output:
                for t in output['newTasks']:
                    # get a taskId from my manager
                    self.m.packTask(t)
                    self.signTask(t)
                    self.m.addTask(t)
                    # add it in my manager's queue
        if isOK and task.status != 'failed':
            task.status = 'done'
            myLogger.info("OK in parsing, set task[%d] done" % (task.id))
        else:
            task.status = 'failed'
        # put it in the outPQueue
        self.outPQueue.put(task)



if __name__ == '__main__':
    print 'hello world'

