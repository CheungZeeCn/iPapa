#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-01-26 16:19:45 
# Copyright 2014 NONE rights reserved.
# thanks for http://www.the5fire.com/python-thread-pool.html

import Queue
import threading
import time
from iWorker import Worker
from iController import Controller
from iParser import Parser
import logging
import util
from setup import iPapa
import os
import json
# a Counter class with lock
from mCounter import mCounter
import sys


myLogger = None
if 'iPapa_manager' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_manager')

class WorkManager(object):
    def __init__(self, seedTask, threadNum=2, parserNum=2, isReRun=False):
        self.returnVal = True
        # not implemented now, set it true for crash recover
        self.isReRun = isReRun
        self.sign = 'manager'
        # queues for download
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()
        # queues for parse
        self.inPQueue = self.outQueue
        self.outPQueue = Queue.Queue()
        self.wThreads = []
        self.pThreads = []
        # controller provides interfaces for human beings
        self.cThread = None

        #self.initTasks = []
        #self.tasksDone = []
        #taskCounter for giving id to each task
        self.taskCounter = mCounter(0)
        self.taskDoneCounter = mCounter(0)
        self.taskFailedCounter = mCounter(0)
        self.taskIgnoreCounter = mCounter(0)
        # activeTasks is only a pool for monitoring the tasks
        self.activeTasks = []
        self.myLock = threading.Lock()
        # init threads and tasks
        self.__init_wThread_pool(threadNum)
        self.__init_pThread_pool(parserNum)
        self.__init_control_thread() # init self.cThread
        self.init(seedTask)
        # about running
        self.timeStampBegin = time.time()
        self.timeStampStr = util.getTimeStamp()
        self.shouldExit = False
        # todo, not implemented
        self.whatWeHave = {} 
        self.__set_tsOutputPath()
    
    def __set_tsOutputPath(self):
        tsOutputPath = os.path.join(iPapa.iOutputPath, self.timeStampStr)       
        iPapa.iTsOutputPath = tsOutputPath

    def __init_wThread_pool(self, threadNum):
        """
        init the thread pool, assign thread ids to them
        """
        for i in range(threadNum):
            self.wThreads.append(Worker(str(i), self))
        # OK! we init all the wThreads 
        return True

    def __init_pThread_pool(self, threadNum):
        """
        init the thread pool, assign thread ids to them
        """
        for i in range(threadNum):
            self.pThreads.append(Parser(str(i), self))
        # OK! we init all the wThreads 
        return True

    def __init_control_thread(self):
        """
        ///to be updated
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
        self.taskDoneCounter.inc()
        return True

    def initWhatWeHave(self):
        if self.isReRun == True: # return to my last life
            self.whatWeHave = findoutWhatWeHave()
        else:
            self.whatWeHave = {}

    def init(self, seedTask):
        # todo support tasks in init
        self.initWhatWeHave()
        self.initTasksInQueue(seedTask) 

    def initTasksInQueue(self, seedTask):
        #sign it
        self.packTask(seedTask)
        self.signTask(seedTask)
        self.addTask(seedTask)
        myLogger.info("initTasksInQueue Done, seedTask is: [%s]"  % (seedTask.id))

    def signTask(self, task):
        task.handleBy = self.sign
        task.signTs.append((task.handleBy, time.time())) 

    def addTask(self, task):
        myLogger.info("addTask [%s]"  % (task.id))
        self.inQueue.put(task)
        with self.myLock:
            self.activeTasks.append(task)

    def rmTask(self, task):
        # make sure the task is out of the queue 
        # before we call the rmTask()
        with self.myLock:
            for i in range(len(self.activeTasks)):
                if self.activeTasks[i].id == task.id:
                    del(self.activeTasks[i])
                    break
        return True      

    def packTask(self, task):
        #set the id for a task
        newId = self.taskCounter.inc()
        task.id = newId
        return task

    def isAllDone(self):
        # check inQueue
        #if self.inQueue.qsize() != 0:
        #    print self.inQueue.qsize()
        #    return False
        # check if all work is Done 
        isAllDone = True
        for t in self.wThreads:
            if t.isAlive() and t.isHungerly() == False:
                isAllDone = False    
                break
        for t in self.pThreads:
            if t.isAlive() and t.isHungerly() == False:
                isAllDone = False    
                break
        return isAllDone

    def exit(self):
        self.logStatus()   
        self.shouldExit = True
        # wait for all 
        for t in self.wThreads:
            tId = t.name
            t.join()
            myLogger.info("worker thread [%s] joined" % (tId))
        for t in self.pThreads:
            tId = t.name
            t.join()
            myLogger.info("parser thread [%s] joined" % (tId))
        self.logStatus()
        myLogger.info("all worker/parser threads have been joined, exit!")
        if self.returnVal != True: 
            sys.exit("[iPapa] Not ALL task finished, plz check it.")


    def flushOutPQueue(self):
        while not self.outPQueue.empty():
            ret = self.outPQueue.get()
            self.dealWithParserOutput(ret)
        myLogger.info('flushOutPQueue Done, outPQueue empty guaranteed.')
        return True     

    def genStatus(self):
        report = {}
        report['status_data']=[]
        for t in self.wThreads:
            name = t.name
            idle = t.isHungerly()
            alive = t.isAlive()
            report['status_data'].append({'wThread_name':name, 'is_idle':idle, 'is_alive':alive})
        for t in self.pThreads:
            name = t.name
            idle = t.isHungerly()
            alive = t.isAlive()
            report['status_data'].append({'pThread_name':name, 'is_idle':idle, 'is_alive':alive})
        activeCount = threading.activeCount()
        report['all_thread_activeCount'] = activeCount
        # todo make it more clear here
        report['active_tasks'] = [ [t.id, t.status, t.url ] for t in self.activeTasks]

        report['length_of_inQueue'] = self.inQueue.qsize()
        report['length_of_outQueue'] = self.outQueue.qsize()
        report['length_of_inPQueue'] = self.inPQueue.qsize()
        report['length_of_outPQueue'] = self.outPQueue.qsize()
        runLog = {'timeBeginStr': self.timeStampStr , 
                    'running_duration(seconds)': time.time() - self.timeStampBegin,
                    'task_done_counter': self.taskDoneCounter.get(),
                    'task_failed_counter': self.taskFailedCounter.get(),
                    'task_ignore_counter': self.taskIgnoreCounter.get(),
                    'task_all_counter': self.taskCounter.get(),
                    }
        report['runLog'] = runLog
        return report

    def logStatus(self):
        report = self.genStatus()
        myLogger.info("STATUS: %s" % (json.dumps(report)))

    def dealWithParserOutput(self, task):
        if task.status == 'done':
            #counters
            self.taskDoneCounter.inc()
            self.rmTask(task)
            #print "task id %s done" % (task.id)
            myLogger.info("task [%d] Done [%s]" % (task.id, task.exprMe()))
            task['__expr__'] = task.exprMe()
            fileName = os.path.join(iPapa.iTsOutputPath, "doneTask.%d.json" % task.id)
            util.dump2JsonFile(task['__expr__'], fileName)
        elif task.status == 'ignore':
            self.taskIgnoreCounter.inc()
            self.rmTask(task)
            #print "task id %s done" % (task.id)
            myLogger.info("task [%d] Ignored [%s]" % (task.id, task.exprMe()))
            task['__expr__'] = task.exprMe()
            fileName = os.path.join(iPapa.iTsOutputPath, "ignoreTask.%d.json" % task.id)
            util.dump2JsonFile(task['__expr__'], fileName)
            
        else:
            #counters
            self.returnVal = False
            self.taskFailedCounter.inc()
            self.rmTask(task)
            myLogger.error("task [%d] Failed [%s], dump it" % (task.id, task.exprMe()))
            task['__expr__'] = task.exprMe()
            fileName = os.path.join(iPapa.iTsOutputPath, "failedTask.%d.json" % task.id)
            util.dump2JsonFile(task, fileName)
            # todo :if we want to support the repeat argument
            #  take care of the function flush
        pass

    def start(self):
        """
        start control thread, worker threads, then the manager keep waiting for the output
        """
        # start control thread
        self.cThread.start()
        # start workers
        for i in range(len(self.wThreads)):
            self.wThreads[i].start()  
        # start parsers
        for i in range(len(self.pThreads)):
            self.pThreads[i].start()  
        #time.sleep(1)
        nowMin = int(time.time()) / 60
        lastMin = nowMin
        # start waiting for output
        isAllDone = False
        while True:
            ret = None
            # timeout
            try:
                # keep blocked until timeout secs passed.
                ret = self.outPQueue.get(timeout=5)
                self.dealWithParserOutput(ret)
            except Queue.Empty, e:
                myLogger.debug('outPQueue Empty, will check whether all tasks are Done')
                # if all the threads(not dead) are hungerly
                isAllDone = self.isAllDone()
            # all worker threads have nothing to do ?
            if isAllDone == False:         
                myLogger.debug("Manger: I get nothing from outPQueue, but some worker thread are busy")
                nowMin = int(time.time()) / 60
                if nowMin > lastMin:
                    lastMin = nowMin 
                    self.logStatus()   
                #time.sleep(1)
            else:# all done here.
                # check it for rest
                self.logStatus()
                self.flushOutPQueue()
                break # ready for exit
        myLogger.info("All tasks completed, about to exit.")
        self.exit()

if __name__ == '__main__':
    pass
