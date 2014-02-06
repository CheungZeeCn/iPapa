#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-01-26 16:19:45 
# Copyright 2014 NONE rights reserved.
# thanks for http://www.the5fire.com/python-thread-pool.html

import Queue
import threading
import time
from iWorker import Worker, Controller
import logging
import util
from setup import iPapa
import os


myLogger = None
if 'iPapa_manager' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_manager')

class WorkManager(object):
    def __init__(self, threadNum=2):
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()
        self.wThreads = []
        self.cThread = None
        self.initTasks = []
        #self.tasksDone = []
        self.__init_wThread_pool(threadNum)
        self.__init_control_thread() # init self.cThread
        self.init()
        # about running
        self.timeStampBegin = time.time()
        self.taskDoneCounter = 0
        self.myLock = threading.Lock()
        self.timeStamp = util.getTimeStamp()

    def __init_wThread_pool(self, threadNum):
        """
        init the thread pool, assign thread ids to them
        """
        for i in range(threadNum):
            self.wThreads.append(Worker(str(i), self))
        # OK! we init all the wThreads 
        return True

    def __init_control_thread(self):
        """
        we init the control thread here for:
            1. asking status
                11. How many threads
                12. The status for each threads, timestamp or \
                    something like that
                13. The leangths for inQueue and outQueue
                14. The running times(duration, timeBegin...).
            2. doing some controlling works by \
                http interfaces(nothing implemented now, to do)
        """
        self.cThread = Controller(self)
        pass

    def oneTaskDone(self):
        if self.myLock.acquire():
            self.taskDoneCounter += 1 
            self.myLock.release()
            return True
        return False

    def init(self):
        self.initTasksInQueue() 

    def getTaskFromFile(self):
        fName = os.path.join(iPapa.iDataPath, 'zl.list')   
        taskDict = {}
        with open(fName) as f:
            for each in f:
                each = each.decode('utf-8')      
                each = each.strip()
                each = each.split(" ")
                taskDict[each[0]] = each[1]
        return taskDict

    def initTasksInQueue(self):
        """
        we can modify this function for different tasks' inition
            1. init self.tasks, which can be shown \
                by control thread
            2. put sth in self.inQueue
            3. set empty in self.ok

        task structure:
            {
                'id': id,  #assigned by input file or manager
                'inData': inData, # input, can be any type 
                'outData': outData, # output, can be any type
                'status': status, #'OK', 'ERROR', 'None'
                'msg': 'default' 
            } 

        """
        tasksDict = self.getTaskFromFile()
        for k in tasksDict:
            task = {
                'id': k,  #assigned by input file or manager
                'inData': tasksDict[k], # input, can be any type 
                'outData': None, # output, can be any type
                'status': 'NONE', #'OK', 'ERROR', 'NONE', 
                'msg': 'IN QUEUE' 
            }
            self.initTasks.append(task)

        for i in self.initTasks:
            self.inQueue.put(i)
        myLogger.info("initTasksInQueue Done. self.initTasks:[%s] qsize[%d]" % (self.initTasks, self.inQueue.qsize()))
        pass

    def isAllDone(self):
        # check inQueue
        #if self.inQueue.qsize() != 0:
        #    print self.inQueue.qsize()
        #    return False
        # check if all work is Done 
        isAllDone = True
        for t in self.wThreads:
            if t.isHungerly() == False:
                isAllDone = False    
                break
        return isAllDone

    def exit(self):
        pass

    def dealWithOutput(self, output):
        """
        task(output) structure:
            {
                'id': id,  #assigned by input file or manager
                'inData': inData, # input, can be any type 
                'outData': outData, # output, can be any type
                'status': status, #'OK', 'ERROR', 'None'
                'msg': 'default' 
            } 
        """
        myLogger.info('get output: [%s]' % (output))
        # check status
        theId = output['id']
        kw = output['inData']
        msg = output['msg']
        if output['status'] == 'ERROR':
            myLogger.error('id[%s], kw[%s], sth_wrong[%s]' % (theId, kw, msg)) 
        elif output['status'] == 'NONE':
            myLogger.warn('id[%s], kw[%s], sth_sad[%s]' % (theId, kw, msg)) 
        else: # OK
            #write it down in output dir
            stamp = self.timeStamp
            outputPath = iPapa.iOutputPath 
            outputFile = os.path.join(outputPath, "%s_%s_%s" % (stamp, output['id'], kw))
            # 
            util.dump2JsonFile(output, outputFile)
            myLogger.info('id[%s], kw[%s], OK[%s]' % (theId, kw, msg)) 
        self.oneTaskDone()

    def flushOutQueue(self):
        while not self.outQueue.empty():
            ret = self.outQueue.get()
            self.dealWithOutput(ret)
        myLogger.info('flushOutQueue Done, outQueue empty guaranteed.')
        return True     

    def start(self):
        """
        start control thread, worker threads, then the manager keep waiting for the output
        """
        # strat control thread
        self.cThread.start()
        # start workers
        for i in range(len(self.wThreads)):
            self.wThreads[i].start()  
        #time.sleep(1)
        # start waiting for output
        isAllDone = False
        while True:
            ret = None
            # timeout
            try:
                # keep blocked until 2 secs passed.
                ret = self.outQueue.get(timeout=2)
                self.dealWithOutput(ret)
            except Queue.Empty, e:
                myLogger.debug('outQueue Empty, will check whether all tasks are Done')
                isAllDone = self.isAllDone()
            # all worker threads have nothing to do ?
            if isAllDone == False:         
                myLogger.debug("Manger: I get nothing from outQueue, but some worker thread are busy")
                #time.sleep(1)
            else:# all done here.
                # check it for rest
                self.flushOutQueue()
                break # ready for exit
        myLogger.info("All tasks completed, exit.")
        self.exit()

if __name__ == '__main__':
    initLog()
    m = WorkManager(2)
    m.start()

